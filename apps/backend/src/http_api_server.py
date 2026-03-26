"""Local HTTP API server for dataset discovery endpoint verification."""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections.abc import Callable, Mapping
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from typing import Any
from urllib.parse import parse_qs, urlparse

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool

from src.contract.errors import ContractQueryError
from src.contract.query.dataset_discovery_contracts import (
    dataset_not_found_error,
    invalid_request_error,
)
from src.query.dataset_catalog_query import execute_dataset_catalog
from src.query.dataset_detail_query import execute_dataset_detail
from src.query.dataset_discovery_persisted_repository import (
    PersistedDatasetDiscoveryRepository,
)
from src.query.dataset_discovery_service import DatasetDiscoveryService
from src.query.dataset_recent_updates_query import execute_recent_updates
from src.query.dataset_search_query import execute_dataset_search
from src.query.dataset_search_suggestions_query import execute_dataset_search_suggestions
from src.query.dataset_search_summary_query import execute_search_summary


def _env_value(environment: Mapping[str, str], key: str, default: str) -> str:
    value = environment.get(key)
    if value is None or value == "":
        return default
    return value


def _resolve_database_url(*, environment: Mapping[str, str]) -> str:
    explicit_database_url = environment.get("DATABASE_URL")
    if explicit_database_url:
        return explicit_database_url
    user = _env_value(environment, "LOCAL_DB_USER", "longtail")
    password = _env_value(environment, "LOCAL_DB_PASSWORD", "longtail")
    host = _env_value(environment, "LOCAL_DB_HOST", "127.0.0.1")
    port = _env_value(environment, "LOCAL_DB_PORT", "55432")
    name = _env_value(environment, "LOCAL_DB_NAME", "longtail_local")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


def _require_schema_readiness(*, engine: Any, expected_revision: str) -> None:
    try:
        with engine.connect() as connection:
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version LIMIT 1")
            ).scalar_one_or_none()
    except SQLAlchemyError as exc:
        raise RuntimeError("Runtime database schema is not ready") from exc

    if revision is None:
        raise RuntimeError("Runtime database schema version is missing")
    if str(revision) != expected_revision:
        raise RuntimeError(
            "Runtime database schema revision mismatch: "
            f"expected {expected_revision}, got {revision}"
        )


def _make_service() -> DatasetDiscoveryService:
    expected_revision = os.environ.get(
        "DISCOVERY_EXPECTED_DB_REVISION",
        "0009_drop_source_profile_frequency",
    )
    database_url = _resolve_database_url(environment=os.environ)
    engine = create_engine(database_url, pool_pre_ping=True, poolclass=NullPool)
    _require_schema_readiness(engine=engine, expected_revision=expected_revision)
    repository = PersistedDatasetDiscoveryRepository(engine=engine)
    return DatasetDiscoveryService(repository)


class DatasetApiHandler(BaseHTTPRequestHandler):
    """HTTP handler exposing dataset discovery and detail endpoints."""

    service: DatasetDiscoveryService | None = None

    def _write_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_csv(self, *, status: int, body: str, dataset_id: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{dataset_id}.csv"')
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _handle_search(
        self, query: dict[str, list[str]], service: DatasetDiscoveryService
    ) -> dict[str, object]:
        q = query.get("q", [None])[0]
        page = query.get("page", [None])[0]
        page_size = query.get("page_size", [None])[0]
        return execute_dataset_search(
            service,
            query_text=q,
            page=int(page) if page is not None else None,
            page_size=int(page_size) if page_size is not None else None,
        ).model_dump()

    def _handle_summary(self, service: DatasetDiscoveryService) -> dict[str, object]:
        return execute_search_summary(service).model_dump()

    def _handle_suggestions(
        self, query: dict[str, list[str]], service: DatasetDiscoveryService
    ) -> dict[str, object]:
        q = query.get("q", [None])[0]
        limit = query.get("limit", [None])[0]
        return execute_dataset_search_suggestions(
            service,
            query_text=q,
            limit=int(limit) if limit is not None else None,
        ).model_dump()

    def _handle_recent(
        self, query: dict[str, list[str]], service: DatasetDiscoveryService
    ) -> dict[str, object]:
        limit = query.get("limit", [None])[0]
        return execute_recent_updates(
            service,
            limit=int(limit) if limit is not None else None,
        ).model_dump()

    def _handle_catalog(
        self, query: dict[str, list[str]], service: DatasetDiscoveryService
    ) -> dict[str, object]:
        q = query.get("q", [None])[0]
        source_id = query.get("source_id", [None])[0]
        page = query.get("page", [None])[0]
        page_size = query.get("page_size", [None])[0]
        group_by_source = query.get("group_by_source", ["false"])[0].lower() == "true"
        return execute_dataset_catalog(
            service,
            query_text=q,
            source_id=source_id,
            page=int(page) if page is not None else None,
            page_size=int(page_size) if page_size is not None else None,
            group_by_source=group_by_source,
        ).model_dump()

    def _handle_detail(
        self,
        parsed_path: str,
        query: dict[str, list[str]],
        service: DatasetDiscoveryService,
    ) -> dict[str, object]:
        dataset_id = parsed_path.split("/", maxsplit=3)[3]
        return execute_dataset_detail(
            service,
            dataset_id=dataset_id,
            from_date=query.get("from_date", [None])[0],
            to_date=query.get("to_date", [None])[0],
        ).model_dump()

    def _handle_csv(
        self,
        parsed_path: str,
        query: dict[str, list[str]],
        service: DatasetDiscoveryService,
    ) -> tuple[str, str]:
        dataset_id = parsed_path.split("/", maxsplit=3)[3][: -len(".csv")]
        detail_payload = execute_dataset_detail(
            service,
            dataset_id=dataset_id,
            from_date=query.get("from_date", [None])[0],
            to_date=query.get("to_date", [None])[0],
        ).model_dump()

        observations = detail_payload.get("observations", [])
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["observed_on", "value", "reported_at", "attributes"])

        if isinstance(observations, list):
            for observation in observations:
                if not isinstance(observation, dict):
                    continue
                writer.writerow(
                    [
                        str(observation.get("observed_on", "")),
                        observation.get("value", ""),
                        str(observation.get("reported_at", "")),
                        json.dumps(observation.get("attributes", {}), separators=(",", ":")),
                    ]
                )

        return dataset_id, output.getvalue()

    def _dispatch_get(
        self,
        *,
        path: str,
        query: dict[str, list[str]],
        service: DatasetDiscoveryService,
    ) -> tuple[HTTPStatus, dict[str, object]]:
        exact_routes: dict[str, Callable[[], dict[str, object]]] = {
            "/api/health": lambda: {"status": "ok"},
            "/api/datasets/search": lambda: self._handle_search(query, service),
            "/api/datasets/search/summary": lambda: self._handle_summary(service),
            "/api/datasets/search/suggestions": lambda: self._handle_suggestions(query, service),
            "/api/datasets/recent": lambda: self._handle_recent(query, service),
            "/api/datasets": lambda: self._handle_catalog(query, service),
        }

        if path in exact_routes:
            return HTTPStatus.OK, exact_routes[path]()
        if path.startswith("/api/datasets/"):
            return HTTPStatus.OK, self._handle_detail(path, query, service)
        return HTTPStatus.NOT_FOUND, {
            "error": {"code": "not_found", "message": "Endpoint not found"}
        }

    def do_GET(self) -> None:
        """Handle read-only dataset discovery API requests."""
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if self.service is None:
            self._write_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                invalid_request_error("service_not_initialized").model_dump(),
            )
            return

        try:
            if parsed.path.startswith("/api/datasets/") and parsed.path.endswith(".csv"):
                dataset_id, csv_body = self._handle_csv(parsed.path, query, self.service)
                self._write_csv(status=HTTPStatus.OK, body=csv_body, dataset_id=dataset_id)
                return

            response_status, response_payload = self._dispatch_get(
                path=parsed.path,
                query=query,
                service=self.service,
            )
        except ContractQueryError as exc:
            if str(exc) == "dataset_not_found":
                dataset_id = parsed.path.split("/")[-1]
                if dataset_id.endswith(".csv"):
                    dataset_id = dataset_id[: -len(".csv")]
                response_status = HTTPStatus.NOT_FOUND
                response_payload = dataset_not_found_error(dataset_id).model_dump()
            else:
                response_status = HTTPStatus.BAD_REQUEST
                response_payload = invalid_request_error(str(exc)).model_dump()
        except ValueError as exc:
            response_status = HTTPStatus.BAD_REQUEST
            response_payload = invalid_request_error(str(exc)).model_dump()

        self._write_json(response_status, response_payload)


def main() -> None:
    """Run the local dataset API verification server."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    DatasetApiHandler.service = _make_service()
    server = ThreadingHTTPServer((args.host, args.port), DatasetApiHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
