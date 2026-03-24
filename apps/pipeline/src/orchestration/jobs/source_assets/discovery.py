"""
Source discovery utilities for source-asset runtime registration.

NOTE (Feature 011): Source cadence metadata in SourceSchedulePolicy attached to
registrations is now used for operator visibility only. Active scheduling authority
is owned by per-source Dagster schedule definitions in source_asset_schedules.py.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Protocol, cast

from ..source_ingest_runner import SourceIngestRunner
from ..source_schedule_policy import CadenceType, SourceSchedulePolicy
from ..workflow_registry import SourceWorkflowRegistration
from .series_catalog import SeriesCatalogEntry

ADAPTER_PACKAGE_NAME = "src.orchestration.jobs.sources"
CRON_FIELD_COUNT = 5


class ObservationCheckpointRepository(Protocol):
    """Protocol for reading latest persisted canonical observation dates."""

    def read_latest_observed_on(self, *, series_key: str):
        """Return latest persisted observation date for one canonical series."""


@dataclass(frozen=True)
class SourceAdapterManifestError(ValueError):
    """Raised when one or more adapter manifests violate startup contract rules."""

    violations: tuple[str, ...]

    def __str__(self) -> str:
        """Render all module-scoped manifest violations in one startup error."""
        lines = ["source adapter manifest validation failed:"]
        lines.extend(f"- {violation}" for violation in self.violations)
        return "\n".join(lines)


@dataclass(frozen=True)
class SourceBuilderSpec:
    """One discoverable source workflow builder declaration."""

    source_key: str
    module_name: str
    builder: Callable[..., SourceWorkflowRegistration]
    provider_group_key: str = ""
    series_item_keys: tuple[str, ...] = ()
    canonical_series_keys: tuple[str, ...] = ()
    ownership_mode: str = "grouped"
    cron_schedule: str = "0 * * * *"
    cadence_label: CadenceType = "hourly"


def is_adapter_spec(spec: SourceBuilderSpec) -> bool:
    """Return True when a spec is eligible for adapter registration discovery."""
    module_name = spec.module_name.strip()
    source_key = spec.source_key.strip()
    if not module_name or not source_key:
        return False
    # Adapter modules follow the *_source naming contract in this repository.
    return module_name.rsplit(".", 1)[-1].endswith("_source")


def filter_adapter_specs(
    specs: tuple[SourceBuilderSpec, ...],
) -> tuple[list[SourceBuilderSpec], list[SourceBuilderSpec]]:
    """Split specs into eligible adapter specs and ignored non-adapter specs."""
    eligible: list[SourceBuilderSpec] = []
    ignored: list[SourceBuilderSpec] = []
    for spec in specs:
        if is_adapter_spec(spec):
            eligible.append(spec)
        else:
            ignored.append(spec)
    return eligible, ignored


def _build_default_specs() -> tuple[SourceBuilderSpec, ...]:
    return scan_adapter_modules()


def reset_adapter_module_scan_cache_for_tests() -> None:
    """Reset scan cache for deterministic test isolation."""
    _scan_adapter_modules_cached.cache_clear()


def scan_adapter_modules() -> tuple[SourceBuilderSpec, ...]:
    """Scan adapter modules and return validated specs in deterministic order."""
    return _scan_adapter_modules_cached()


@lru_cache(maxsize=1)
def _scan_adapter_modules_cached() -> tuple[SourceBuilderSpec, ...]:
    """Memoized module scan to avoid repeated import and validation work."""
    package = importlib.import_module(ADAPTER_PACKAGE_NAME)
    package_path = getattr(package, "__path__", None)
    if package_path is None:
        raise SourceAdapterManifestError(
            violations=(
                _violation(
                    module_name=ADAPTER_PACKAGE_NAME,
                    source_key="<scan>",
                    reason="adapter package is not scannable",
                ),
            )
        )

    specs: list[SourceBuilderSpec] = []
    errors: list[str] = []
    for module_info in pkgutil.iter_modules(package_path, prefix=f"{ADAPTER_PACKAGE_NAME}."):
        module_name = module_info.name
        if not module_name.rsplit(".", 1)[-1].endswith("_source"):
            continue

        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            errors.append(
                _violation(
                    module_name=module_name,
                    source_key="<import>",
                    reason=f"module import failed ({exc})",
                )
            )
            continue

        try:
            spec = _build_source_builder_spec(module_name=module_name, module=module)
            specs.append(spec)
        except SourceAdapterManifestError as exc:
            errors.extend(exc.violations)

    duplicate_errors = _find_duplicate_source_key_errors(specs)
    if duplicate_errors:
        errors.extend(duplicate_errors)

    if errors:
        raise SourceAdapterManifestError(violations=tuple(errors))

    return tuple(sorted(specs, key=lambda spec: spec.source_key))


def _build_source_builder_spec(*, module_name: str, module: Any) -> SourceBuilderSpec:
    raw_spec = getattr(module, "SOURCE_SPEC", None)
    if not isinstance(raw_spec, dict):
        raise SourceAdapterManifestError(
            violations=(
                _violation(
                    module_name=module_name,
                    source_key="<missing>",
                    reason="SOURCE_SPEC must be defined as a dict",
                ),
            )
        )

    violations: list[str] = []

    source_key = _as_non_empty_str(raw_spec.get("source_key"))
    if source_key is None:
        violations.append(
            _violation(
                module_name=module_name,
                source_key="<missing>",
                reason="source_key must be non-empty",
            )
        )
        source_key = "<missing>"

    provider_group_key = _as_non_empty_str(raw_spec.get("provider_group_key"))
    if provider_group_key is None:
        violations.append(
            _violation(
                module_name=module_name,
                source_key=source_key,
                reason="provider_group_key must be non-empty",
            )
        )

    cron_schedule = _as_non_empty_str(raw_spec.get("cron_schedule"))
    if cron_schedule is None:
        violations.append(
            _violation(
                module_name=module_name,
                source_key=source_key,
                reason="cron_schedule must be non-empty",
            )
        )
    elif not _is_valid_cron_schedule(cron_schedule):
        violations.append(
            _violation(
                module_name=module_name,
                source_key=source_key,
                reason=f"cron_schedule is invalid ({cron_schedule})",
            )
        )

    cadence_label = _as_cadence_type(raw_spec.get("cadence_label"))
    if cadence_label is None:
        violations.append(
            _violation(
                module_name=module_name,
                source_key=source_key,
                reason=("cadence_label must be one of hourly,daily,weekly,monthly,custom_interval"),
            )
        )

    ownership_mode = _as_non_empty_str(raw_spec.get("ownership_mode")) or "grouped"
    if ownership_mode not in {"grouped", "split"}:
        violations.append(
            _violation(
                module_name=module_name,
                source_key=source_key,
                reason="ownership_mode must be grouped or split",
            )
        )

    series_item_keys = _as_non_empty_str_tuple(raw_spec.get("series_item_keys"))
    canonical_series_keys = _as_non_empty_str_tuple(raw_spec.get("canonical_series_keys"))
    if not series_item_keys:
        violations.append(
            _violation(
                module_name=module_name,
                source_key=source_key,
                reason="series_item_keys must contain at least one key",
            )
        )
    if not canonical_series_keys:
        violations.append(
            _violation(
                module_name=module_name,
                source_key=source_key,
                reason="canonical_series_keys must contain at least one key",
            )
        )
    if (
        series_item_keys
        and canonical_series_keys
        and len(series_item_keys) != len(canonical_series_keys)
    ):
        violations.append(
            _violation(
                module_name=module_name,
                source_key=source_key,
                reason="series_item_keys and canonical_series_keys length mismatch",
            )
        )

    builder = raw_spec.get("builder")
    if not callable(builder):
        violations.append(
            _violation(
                module_name=module_name,
                source_key=source_key,
                reason="builder must be callable",
            )
        )

    if violations:
        raise SourceAdapterManifestError(violations=tuple(violations))

    assert provider_group_key is not None
    assert cron_schedule is not None
    assert cadence_label is not None

    return SourceBuilderSpec(
        source_key=source_key,
        module_name=module_name,
        builder=builder,
        provider_group_key=provider_group_key,
        series_item_keys=series_item_keys,
        canonical_series_keys=canonical_series_keys,
        ownership_mode=ownership_mode,
        cron_schedule=cron_schedule,
        cadence_label=cadence_label,
    )


def _find_duplicate_source_key_errors(specs: list[SourceBuilderSpec]) -> list[str]:
    by_source_key: dict[str, list[str]] = {}
    for spec in specs:
        by_source_key.setdefault(spec.source_key, []).append(spec.module_name)

    errors: list[str] = []
    for source_key, module_names in by_source_key.items():
        if len(module_names) <= 1:
            continue
        names = ", ".join(sorted(module_names))
        errors.append(
            _violation(
                module_name=names,
                source_key=source_key,
                reason="duplicate source_key declared by multiple modules",
            )
        )
    return errors


def _violation(*, module_name: str, source_key: str, reason: str) -> str:
    return f"module={module_name} source_key={source_key} reason={reason}"


def _as_non_empty_str(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _as_non_empty_str_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            return ()
        token = item.strip()
        if not token:
            return ()
        normalized.append(token)
    return tuple(normalized)


def _as_cadence_type(value: Any) -> CadenceType | None:
    normalized = _as_non_empty_str(value)
    if normalized in {"hourly", "daily", "weekly", "monthly", "custom_interval"}:
        return cast(CadenceType, normalized)
    return None


def _is_valid_cron_schedule(value: str) -> bool:
    fields = value.split()
    if len(fields) != CRON_FIELD_COUNT:
        return False

    # Keep startup validation lightweight while rejecting malformed expressions.
    token_pattern = re.compile(r"^[\d\*/,\-]+$")
    for token in fields:
        if token == "*":
            continue
        if not token_pattern.fullmatch(token):
            return False
    return True


def discover_source_registrations(
    *,
    runner: SourceIngestRunner,
    observation_repository: ObservationCheckpointRepository,
    specs: tuple[SourceBuilderSpec, ...] | None = None,
) -> list[tuple[str, SourceWorkflowRegistration]]:
    """Discover and build source registrations in deterministic source-key order."""
    discovered_specs = specs or _build_default_specs()
    eligible_specs, _ignored_specs = filter_adapter_specs(discovered_specs)
    by_source_key = sorted(eligible_specs, key=lambda spec: spec.source_key)

    registrations: list[tuple[str, SourceWorkflowRegistration]] = []
    for spec in by_source_key:
        registration = _build_registration_from_spec(
            spec=spec,
            runner=runner,
            observation_repository=observation_repository,
        )
        registrations.append((spec.module_name, registration))

    return registrations


def discover_series_catalog_entries(
    *,
    specs: tuple[SourceBuilderSpec, ...] | None = None,
) -> list[SeriesCatalogEntry]:
    """Discover runtime series catalog entries from source builder specs."""
    discovered_specs = specs or _build_default_specs()
    eligible_specs, _ignored_specs = filter_adapter_specs(discovered_specs)
    by_source_key = sorted(eligible_specs, key=lambda spec: spec.source_key)
    entries: list[SeriesCatalogEntry] = []
    for spec in by_source_key:
        if spec.series_item_keys and spec.canonical_series_keys:
            pairs = zip(spec.series_item_keys, spec.canonical_series_keys, strict=True)
            for series_item_key, canonical_series_key in pairs:
                entries.append(
                    SeriesCatalogEntry(
                        source_key=spec.source_key,
                        provider_group_key=(spec.provider_group_key or spec.source_key),
                        series_item_key=series_item_key,
                        canonical_series_key=canonical_series_key,
                        ownership_mode=spec.ownership_mode,
                    )
                )
            continue

        entries.append(
            SeriesCatalogEntry(
                source_key=spec.source_key,
                provider_group_key=(spec.provider_group_key or spec.source_key),
                series_item_key=spec.source_key,
                canonical_series_key=spec.source_key,
                ownership_mode=spec.ownership_mode,
            )
        )
    return entries


def _build_registration_from_spec(
    *,
    spec: SourceBuilderSpec,
    runner: SourceIngestRunner,
    observation_repository: ObservationCheckpointRepository,
) -> SourceWorkflowRegistration:
    schedule_policy = SourceSchedulePolicy(
        source_key=spec.source_key,
        cadence_type=spec.cadence_label,
    )
    builder_params = inspect.signature(spec.builder).parameters
    if "schedule_policy" in builder_params:
        return spec.builder(
            runner,
            observation_repository=observation_repository,
            schedule_policy=schedule_policy,
        )
    return spec.builder(runner, observation_repository)
