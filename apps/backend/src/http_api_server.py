"""Local HTTP API server for dataset discovery endpoint verification."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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
        "0008_dataset_discovery_indexes",
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

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """Reduce handler logging noise; keep default behavior minimal."""
        del format, args

    def do_GET(self) -> None:  # noqa: N802
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
            if parsed.path == "/api/health":
                self._write_json(HTTPStatus.OK, {"status": "ok"})
                return

            if parsed.path == "/api/datasets/search":
                q = query.get("q", [None])[0]
                page = query.get("page", [None])[0]
                page_size = query.get("page_size", [None])[0]
                response = execute_dataset_search(
                    self.service,
                    query_text=q,
                    page=int(page) if page is not None else None,
                    page_size=int(page_size) if page_size is not None else None,
                )
                self._write_json(HTTPStatus.OK, response.model_dump())
                return

            if parsed.path == "/api/datasets/recent":
                limit = query.get("limit", [None])[0]
                response = execute_recent_updates(
                    self.service,
                    limit=int(limit) if limit is not None else None,
                )
                self._write_json(HTTPStatus.OK, response.model_dump())
                return

            if parsed.path == "/api/datasets":
                q = query.get("q", [None])[0]
                source_id = query.get("source_id", [None])[0]
                page = query.get("page", [None])[0]
                page_size = query.get("page_size", [None])[0]
                group_by_source = query.get("group_by_source", ["false"])[0].lower() == "true"
                response = execute_dataset_catalog(
                    self.service,
                    query_text=q,
                    source_id=source_id,
                    page=int(page) if page is not None else None,
                    page_size=int(page_size) if page_size is not None else None,
                    group_by_source=group_by_source,
                )
                self._write_json(HTTPStatus.OK, response.model_dump())
                return

            if parsed.path.startswith("/api/datasets/"):
                dataset_id = parsed.path.split("/", maxsplit=3)[3]
                response = execute_dataset_detail(
                    self.service,
                    dataset_id=dataset_id,
                    from_date=query.get("from_date", [None])[0],
                    to_date=query.get("to_date", [None])[0],
                )
                self._write_json(HTTPStatus.OK, response.model_dump())
                return

            self._write_json(
                HTTPStatus.NOT_FOUND,
                {"error": {"code": "not_found", "message": "Endpoint not found"}},
            )
        except ContractQueryError as exc:
            if str(exc) == "dataset_not_found":
                dataset_id = parsed.path.split("/")[-1]
                self._write_json(
                    HTTPStatus.NOT_FOUND,
                    dataset_not_found_error(dataset_id).model_dump(),
                )
            else:
                self._write_json(
                    HTTPStatus.BAD_REQUEST,
                    invalid_request_error(str(exc)).model_dump(),
                )
        except ValueError as exc:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                invalid_request_error(str(exc)).model_dump(),
            )


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
