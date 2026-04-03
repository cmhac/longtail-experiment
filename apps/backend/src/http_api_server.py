"""Local HTTP API server for dataset discovery endpoint verification."""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool

from src.contract.errors import ContractQueryError
from src.contract.query.auth_management_query import (
    conflict_error,
    forbidden_error,
    locked_error,
    not_found_error,
    unauthorized_error,
    validation_error,
)
from src.contract.query.dataset_discovery_contracts import (
    dataset_not_found_error,
    invalid_request_error,
)
from src.contract.query.metadata_discovery_contracts import (
    geography_not_found_error,
    topic_not_found_error,
)
from src.contract.query.source_discovery_contracts import source_not_found_error
from src.query.auth_management_persisted_repository import PersistedAuthManagementRepository
from src.query.auth_management_service import AuthManagementService
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
from src.query.geography_detail_query import execute_geography_detail
from src.query.source_detail_query import execute_source_detail
from src.query.source_list_query import execute_source_list
from src.query.topic_detail_query import execute_topic_detail


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


def _resolve_expected_revision(*, environment: Mapping[str, str]) -> str:
    configured_revision = environment.get("DISCOVERY_EXPECTED_DB_REVISION")
    if configured_revision:
        return configured_revision

    alembic_config_candidates = (
        Path("libs/db/alembic.ini"),
        Path(__file__).resolve().parents[3] / "libs/db/alembic.ini",
    )
    alembic_config_path = next(
        (candidate for candidate in alembic_config_candidates if candidate.exists()),
        None,
    )
    if alembic_config_path is None:
        raise RuntimeError(
            "Unable to resolve expected schema revision: libs/db/alembic.ini was not found"
        )

    try:
        script_directory = ScriptDirectory.from_config(AlembicConfig(str(alembic_config_path)))
        head_revision = script_directory.get_current_head()
    except Exception as exc:  # pragma: no cover - defensive guard around Alembic internals
        raise RuntimeError("Unable to resolve expected schema revision from Alembic head") from exc

    if head_revision is None:
        raise RuntimeError("Unable to resolve expected schema revision: Alembic head is undefined")

    return str(head_revision)


def _optional_int_query_param(query: dict[str, list[str]], key: str) -> int | None:
    value = query.get(key, [None])[0]
    if value is None:
        return None
    return int(value)


def _make_service() -> DatasetDiscoveryService:
    expected_revision = _resolve_expected_revision(environment=os.environ)
    database_url = _resolve_database_url(environment=os.environ)
    engine = create_engine(database_url, pool_pre_ping=True, poolclass=NullPool)
    _require_schema_readiness(engine=engine, expected_revision=expected_revision)
    repository = PersistedDatasetDiscoveryRepository(engine=engine)
    return DatasetDiscoveryService(repository)


def _make_auth_service() -> AuthManagementService:
    expected_revision = _resolve_expected_revision(environment=os.environ)
    database_url = _resolve_database_url(environment=os.environ)
    engine = create_engine(database_url, pool_pre_ping=True, poolclass=NullPool)
    _require_schema_readiness(engine=engine, expected_revision=expected_revision)
    repository = PersistedAuthManagementRepository(engine=engine)
    return AuthManagementService(repository=repository)


class DatasetApiHandler(BaseHTTPRequestHandler):
    """HTTP handler exposing dataset discovery and detail endpoints."""

    service: DatasetDiscoveryService | None = None
    auth_service: AuthManagementService | None = None

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

    def _read_json_body(self) -> dict[str, object]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        payload = self.rfile.read(content_length)
        if payload == b"":
            return {}
        decoded = json.loads(payload.decode("utf-8"))
        if not isinstance(decoded, dict):
            raise ValueError("request body must be a JSON object")
        return decoded

    def _resolve_auth_principal(self, service: AuthManagementService) -> dict[str, object]:
        header_value = self.headers.get("Authorization", "")
        if not header_value.startswith("Bearer "):
            raise ContractQueryError("auth_required")
        session_id = header_value[len("Bearer ") :].strip()
        if session_id == "":
            raise ContractQueryError("auth_required")
        session = service.authenticate_session(session_id=session_id)
        user = session.get("user")
        if not isinstance(user, dict):
            raise ContractQueryError("auth_required")
        principal = dict(user)
        principal["session_id"] = str(session.get("session_id") or session_id)
        return principal

    @staticmethod
    def _require_admin(principal: dict[str, object]) -> None:
        if not bool(principal.get("is_admin") or False):
            raise ContractQueryError("forbidden")

    @staticmethod
    def _auth_contract_error(error: ContractQueryError) -> tuple[HTTPStatus, dict[str, object]]:
        code = str(error)
        mapped_errors: dict[str, tuple[HTTPStatus, dict[str, object]]] = {
            "auth_required": (HTTPStatus.UNAUTHORIZED, unauthorized_error().model_dump()),
            "forbidden": (HTTPStatus.FORBIDDEN, forbidden_error().model_dump()),
            "duplicate_email": (
                HTTPStatus.CONFLICT,
                conflict_error("Account already exists").model_dump(),
            ),
            "account_locked": (
                HTTPStatus.LOCKED,
                locked_error("Account is temporarily locked").model_dump(),
            ),
            "session_not_found": (
                HTTPStatus.NOT_FOUND,
                not_found_error("Session was not found").model_dump(),
            ),
            "invalid_credentials": (
                HTTPStatus.UNAUTHORIZED,
                unauthorized_error("Invalid credentials").model_dump(),
            ),
        }
        return mapped_errors.get(
            code,
            (HTTPStatus.BAD_REQUEST, validation_error(code).model_dump()),
        )

    def _dispatch_auth_get(
        self,
        *,
        path: str,
        service: AuthManagementService,
    ) -> tuple[HTTPStatus, dict[str, object]] | None:
        if path == "/api/auth/sessions":
            principal = self._resolve_auth_principal(service)
            response = service.list_user_sessions(user_id=str(principal["user_id"]))
            return HTTPStatus.OK, response.model_dump()

        if path == "/api/account/profile":
            principal = self._resolve_auth_principal(service)
            return HTTPStatus.OK, {
                "user_id": principal["user_id"],
                "email": principal["email"],
                "display_name": principal.get("display_name"),
                "account_status": principal["account_status"],
                "is_admin": bool(principal.get("is_admin") or False),
                "updated_at": datetime.now(tz=UTC).isoformat(),
            }

        if path == "/api/admin/users":
            principal = self._resolve_auth_principal(service)
            self._require_admin(principal)
            response = service.list_admin_users()
            return HTTPStatus.OK, response.model_dump()

        return None

    def _dispatch_auth_post(
        self,
        *,
        path: str,
        service: AuthManagementService,
    ) -> tuple[HTTPStatus, dict[str, object] | None] | None:
        if path == "/api/auth/sessions":
            return self._dispatch_unified_auth_sessions_post(service=service)

        response_status: HTTPStatus
        response_payload: dict[str, object] | None
        if path == "/api/auth/register":
            payload = self._read_json_body()
            response = service.register_account(
                email=str(payload.get("email") or ""),
                password=str(payload.get("password") or ""),
                display_name=(
                    str(payload["display_name"])
                    if payload.get("display_name") is not None
                    else None
                ),
                client_metadata={"client_label": self.headers.get("User-Agent", "api-client")},
            )
            response_status = HTTPStatus.CREATED
            response_payload = response.model_dump()
        elif path == "/api/auth/login":
            payload = self._read_json_body()
            response = service.login(
                email=str(payload.get("email") or ""),
                password=str(payload.get("password") or ""),
                client_metadata={"client_label": self.headers.get("User-Agent", "api-client")},
            )
            response_status = HTTPStatus.OK
            response_payload = response.model_dump()
        elif path == "/api/auth/logout":
            principal = self._resolve_auth_principal(service)
            service.logout(
                user_id=str(principal["user_id"]),
                session_id=str(principal["session_id"]),
            )
            response_status = HTTPStatus.NO_CONTENT
            response_payload = None
        elif path.startswith("/api/auth/sessions/") and path.endswith("/revoke"):
            principal = self._resolve_auth_principal(service)
            session_id = path.split("/")[-2]
            service.revoke_user_session(user_id=str(principal["user_id"]), session_id=session_id)
            response_status = HTTPStatus.NO_CONTENT
            response_payload = None
        elif path == "/api/account/password":
            principal = self._resolve_auth_principal(service)
            service.repository.revoke_all_sessions_for_user(
                user_id=str(principal["user_id"]), reason="password_changed"
            )
            response_status = HTTPStatus.NO_CONTENT
            response_payload = None
        elif path == "/api/account/deletion-request":
            principal = self._resolve_auth_principal(service)
            deletion_due_at = datetime.now(tz=UTC).replace(microsecond=0).isoformat()
            response_status = HTTPStatus.ACCEPTED
            response_payload = {
                "user_id": principal["user_id"],
                "account_status": "deletion_pending",
                "deletion_due_at": deletion_due_at,
            }
        else:
            return None

        return response_status, response_payload

    def _dispatch_unified_auth_sessions_post(
        self,
        *,
        service: AuthManagementService,
    ) -> tuple[HTTPStatus, dict[str, object] | None]:
        payload = self._read_json_body()
        action = str(payload.get("action") or "").strip().lower()

        if action == "register":
            response = service.register_account(
                email=str(payload.get("email") or ""),
                password=str(payload.get("password") or ""),
                display_name=(
                    str(payload["display_name"])
                    if payload.get("display_name") is not None
                    else None
                ),
                client_metadata={"client_label": self.headers.get("User-Agent", "api-client")},
            )
            return HTTPStatus.CREATED, response.model_dump()

        if action == "login":
            response = service.login(
                email=str(payload.get("email") or ""),
                password=str(payload.get("password") or ""),
                client_metadata={"client_label": self.headers.get("User-Agent", "api-client")},
            )
            return HTTPStatus.OK, response.model_dump()

        if action == "logout":
            principal = self._resolve_auth_principal(service)
            service.logout(
                user_id=str(principal["user_id"]),
                session_id=str(principal["session_id"]),
            )
            return HTTPStatus.NO_CONTENT, None

        if action == "revoke":
            principal = self._resolve_auth_principal(service)
            session_id = str(payload.get("session_id") or "").strip()
            if session_id == "":
                raise ContractQueryError("session_id is required")
            service.revoke_user_session(
                user_id=str(principal["user_id"]),
                session_id=session_id,
            )
            return HTTPStatus.NO_CONTENT, None

        raise ContractQueryError("action must be one of register, login, logout, revoke")

    def _handle_auth_get_route(self, *, path: str) -> bool:
        if self.auth_service is None:
            return False
        try:
            auth_response = self._dispatch_auth_get(path=path, service=self.auth_service)
        except ContractQueryError as exc:
            response_status, response_payload = self._auth_contract_error(exc)
            self._write_json(response_status, response_payload)
            return True
        except ValueError as exc:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                validation_error(str(exc)).model_dump(),
            )
            return True
        if auth_response is None:
            return False

        response_status, response_payload = auth_response
        self._write_json(response_status, response_payload)
        return True

    @staticmethod
    def _discovery_contract_error(
        *, path: str, error: ContractQueryError
    ) -> tuple[HTTPStatus, dict[str, object]]:
        code = str(error)
        not_found_payloads: dict[str, Callable[[str], dict[str, object]]] = {
            "dataset_not_found": lambda value: dataset_not_found_error(value).model_dump(),
            "topic_not_found": lambda value: topic_not_found_error(value).model_dump(),
            "geography_not_found": lambda value: geography_not_found_error(value).model_dump(),
            "source_not_found": lambda value: source_not_found_error(value).model_dump(),
        }
        if code in not_found_payloads:
            entity_id = path.rsplit("/", maxsplit=1)[-1]
            if code == "dataset_not_found" and entity_id.endswith(".csv"):
                entity_id = entity_id[: -len(".csv")]
            return HTTPStatus.NOT_FOUND, not_found_payloads[code](entity_id)

        return HTTPStatus.BAD_REQUEST, invalid_request_error(code).model_dump()

    def _dispatch_auth_patch(
        self,
        *,
        path: str,
        service: AuthManagementService,
    ) -> tuple[HTTPStatus, dict[str, object] | None] | None:
        if path == "/api/account/profile":
            principal = self._resolve_auth_principal(service)
            payload = self._read_json_body()
            display_name = payload.get("display_name")
            return HTTPStatus.OK, {
                "user_id": principal["user_id"],
                "email": principal["email"],
                "display_name": display_name if isinstance(display_name, str) else None,
                "account_status": principal["account_status"],
                "is_admin": bool(principal.get("is_admin") or False),
                "updated_at": datetime.now(tz=UTC).isoformat(),
            }

        if path.startswith("/api/admin/users/") and path.endswith("/status"):
            principal = self._resolve_auth_principal(service)
            self._require_admin(principal)
            user_id = path.split("/")[-2]
            payload = self._read_json_body()
            account_status = str(payload.get("account_status") or "")
            if account_status not in {"active", "deactivated"}:
                raise ContractQueryError("account_status must be active or deactivated")
            return HTTPStatus.OK, {
                "user_id": user_id,
                "email": "",
                "display_name": None,
                "account_status": account_status,
                "is_admin": False,
                "updated_at": datetime.now(tz=UTC).isoformat(),
            }

        return None

    def _handle_search(
        self, query: dict[str, list[str]], service: DatasetDiscoveryService
    ) -> dict[str, object]:
        q = query.get("q", [None])[0]
        page = _optional_int_query_param(query, "page")
        page_size = _optional_int_query_param(query, "page_size")
        return execute_dataset_search(
            service,
            query_text=q,
            page=page,
            page_size=page_size,
        ).model_dump()

    def _handle_summary(self, service: DatasetDiscoveryService) -> dict[str, object]:
        return execute_search_summary(service).model_dump()

    def _handle_suggestions(
        self, query: dict[str, list[str]], service: DatasetDiscoveryService
    ) -> dict[str, object]:
        q = query.get("q", [None])[0]
        limit = _optional_int_query_param(query, "limit")
        return execute_dataset_search_suggestions(
            service,
            query_text=q,
            limit=limit,
        ).model_dump()

    def _handle_recent(
        self, query: dict[str, list[str]], service: DatasetDiscoveryService
    ) -> dict[str, object]:
        limit = _optional_int_query_param(query, "limit")
        return execute_recent_updates(
            service,
            limit=limit,
        ).model_dump()

    def _handle_catalog(
        self, query: dict[str, list[str]], service: DatasetDiscoveryService
    ) -> dict[str, object]:
        q = query.get("q", [None])[0]
        source_id = query.get("source", [None])[0] or query.get("source_id", [None])[0]
        category = query.get("category", [None])[0]
        sort = query.get("sort", [None])[0]
        page = _optional_int_query_param(query, "page")
        page_size = _optional_int_query_param(query, "page_size")
        group_by_source = query.get("group_by_source", ["false"])[0].lower() == "true"
        return execute_dataset_catalog(
            service,
            query_text=q,
            source_id=source_id,
            category=category,
            sort=sort,
            page=page,
            page_size=page_size,
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

    def _handle_source_list(self, service: DatasetDiscoveryService) -> dict[str, object]:
        return execute_source_list(service).model_dump()

    def _handle_source_detail(
        self,
        parsed_path: str,
        query: dict[str, list[str]],
        service: DatasetDiscoveryService,
    ) -> dict[str, object]:
        source_id = parsed_path.split("/", maxsplit=3)[3]
        page = _optional_int_query_param(query, "page")
        page_size = _optional_int_query_param(query, "page_size")
        return execute_source_detail(
            service,
            source_id=source_id,
            page=page,
            page_size=page_size,
        ).model_dump()

    def _handle_topic_detail(
        self,
        parsed_path: str,
        query: dict[str, list[str]],
        service: DatasetDiscoveryService,
    ) -> dict[str, object]:
        topic_id = parsed_path.split("/", maxsplit=3)[3]
        page = _optional_int_query_param(query, "page")
        page_size = _optional_int_query_param(query, "page_size")
        return execute_topic_detail(
            service,
            topic_id=topic_id,
            page=page,
            page_size=page_size,
        ).model_dump()

    def _handle_geography_detail(
        self,
        parsed_path: str,
        query: dict[str, list[str]],
        service: DatasetDiscoveryService,
    ) -> dict[str, object]:
        geography_id = parsed_path.split("/", maxsplit=3)[3]
        page = _optional_int_query_param(query, "page")
        page_size = _optional_int_query_param(query, "page_size")
        return execute_geography_detail(
            service,
            geography_id=geography_id,
            page=page,
            page_size=page_size,
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
            "/api/sources": lambda: self._handle_source_list(service),
            "/api/datasets/search": lambda: self._handle_search(query, service),
            "/api/datasets/search/summary": lambda: self._handle_summary(service),
            "/api/datasets/search/suggestions": lambda: self._handle_suggestions(query, service),
            "/api/datasets/recent": lambda: self._handle_recent(query, service),
            "/api/datasets": lambda: self._handle_catalog(query, service),
        }

        if path in exact_routes:
            return HTTPStatus.OK, exact_routes[path]()
        if path.startswith("/api/sources/"):
            return HTTPStatus.OK, self._handle_source_detail(path, query, service)
        if path.startswith("/api/topics/"):
            return HTTPStatus.OK, self._handle_topic_detail(path, query, service)
        if path.startswith("/api/geographies/"):
            return HTTPStatus.OK, self._handle_geography_detail(path, query, service)
        if path.startswith("/api/datasets/"):
            return HTTPStatus.OK, self._handle_detail(path, query, service)
        return HTTPStatus.NOT_FOUND, {
            "error": {"code": "not_found", "message": "Endpoint not found"}
        }

    def do_GET(self) -> None:
        """Handle read-only dataset discovery API requests."""
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if self._handle_auth_get_route(path=parsed.path):
            return

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
            response_status, response_payload = self._discovery_contract_error(
                path=parsed.path,
                error=exc,
            )
        except ValueError as exc:
            response_status = HTTPStatus.BAD_REQUEST
            response_payload = invalid_request_error(str(exc)).model_dump()

        self._write_json(response_status, response_payload)

    def do_POST(self) -> None:
        """Handle auth/account write endpoints."""
        parsed = urlparse(self.path)
        if self.auth_service is None:
            self._write_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                invalid_request_error("auth_service_not_initialized").model_dump(),
            )
            return

        try:
            auth_response = self._dispatch_auth_post(path=parsed.path, service=self.auth_service)
        except ContractQueryError as exc:
            response_status, response_payload = self._auth_contract_error(exc)
            self._write_json(response_status, response_payload)
            return
        except ValueError as exc:
            self._write_json(HTTPStatus.BAD_REQUEST, validation_error(str(exc)).model_dump())
            return

        if auth_response is None:
            self._write_json(
                HTTPStatus.NOT_FOUND,
                not_found_error("Endpoint not found").model_dump(),
            )
            return

        response_status, response_payload = auth_response
        if response_status == HTTPStatus.NO_CONTENT:
            self.send_response(response_status)
            self.end_headers()
            return
        self._write_json(response_status, response_payload or {})

    def do_PATCH(self) -> None:
        """Handle auth/account patch endpoints."""
        parsed = urlparse(self.path)
        if self.auth_service is None:
            self._write_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                invalid_request_error("auth_service_not_initialized").model_dump(),
            )
            return

        try:
            auth_response = self._dispatch_auth_patch(path=parsed.path, service=self.auth_service)
        except ContractQueryError as exc:
            response_status, response_payload = self._auth_contract_error(exc)
            self._write_json(response_status, response_payload)
            return
        except ValueError as exc:
            self._write_json(HTTPStatus.BAD_REQUEST, validation_error(str(exc)).model_dump())
            return

        if auth_response is None:
            self._write_json(
                HTTPStatus.NOT_FOUND,
                not_found_error("Endpoint not found").model_dump(),
            )
            return

        response_status, response_payload = auth_response
        if response_status == HTTPStatus.NO_CONTENT:
            self.send_response(response_status)
            self.end_headers()
            return
        self._write_json(response_status, response_payload or {})


def main() -> None:
    """Run the local dataset API verification server."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    DatasetApiHandler.service = _make_service()
    DatasetApiHandler.auth_service = _make_auth_service()
    server = ThreadingHTTPServer((args.host, args.port), DatasetApiHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
