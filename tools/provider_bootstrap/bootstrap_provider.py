"""CLI entrypoint for generating provider source adapter scaffolds."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

try:  # pragma: no cover - import resolution boundary for script vs package execution
    from .collision_checks import ensure_output_path_available, ensure_source_key_available
    from .output import BootstrapError, emit_failure, emit_success
    from .render import render_scaffold
    from .validation import (
        normalize_module_name,
        validate_cadence_label,
        validate_canonical_key,
        validate_cron_schedule,
        validate_ownership_mode,
        validate_series_alignment,
        validate_snake_identifier,
    )
except ImportError:  # pragma: no cover
    from collision_checks import ensure_output_path_available, ensure_source_key_available
    from output import BootstrapError, emit_failure, emit_success
    from render import render_scaffold
    from validation import (
        normalize_module_name,
        validate_cadence_label,
        validate_canonical_key,
        validate_cron_schedule,
        validate_ownership_mode,
        validate_series_alignment,
        validate_snake_identifier,
    )

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "apps/pipeline/src/orchestration/jobs/sources"
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates/provider_source_template.py.tmpl"


@dataclass(slots=True)
class BootstrapRequest:
    provider_group_key: str
    source_key: str
    module_name: str
    cadence_label: str
    cron_schedule: str
    series_item_keys: list[str]
    canonical_series_keys: list[str]
    provider_series_ids: list[str]
    provider_name: str
    ownership_mode: str
    output_dir: Path
    metric_name: str
    dataset_description: str
    dataset_geographic_scope: str
    topic_tags: list[str]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap a provider adapter scaffold")
    parser.add_argument("--provider-group-key", required=True)
    parser.add_argument("--source-key", required=True)
    parser.add_argument("--module-name", required=True)
    parser.add_argument("--cadence-label", required=True)
    parser.add_argument("--cron-schedule", required=True)
    parser.add_argument("--series-item-key", action="append", required=True)
    parser.add_argument("--canonical-series-key", action="append", required=True)
    parser.add_argument("--provider-series-id", action="append", required=True)
    parser.add_argument("--provider-name", default="TODO_PROVIDER_NAME")
    parser.add_argument("--metric-name", default="TODO_METRIC_NAME")
    parser.add_argument("--dataset-description", default="TODO_DATASET_DESCRIPTION")
    parser.add_argument("--dataset-geographic-scope", default="TODO_GEOGRAPHIC_SCOPE")
    parser.add_argument("--topic-tags", default="TODO_TOPIC")
    parser.add_argument("--ownership-mode", default="grouped")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser


def parse_request(argv: list[str]) -> BootstrapRequest:
    args = build_parser().parse_args(argv)

    module_stem = normalize_module_name(args.module_name)
    validate_snake_identifier(args.provider_group_key, field="provider_group_key")
    validate_snake_identifier(args.source_key, field="source_key")
    validate_cadence_label(args.cadence_label)
    validate_ownership_mode(args.ownership_mode)
    validate_cron_schedule(args.cron_schedule)
    validate_series_alignment(
        series_item_keys=args.series_item_key,
        canonical_series_keys=args.canonical_series_key,
        provider_series_ids=args.provider_series_id,
    )

    for key in args.series_item_key:
        validate_snake_identifier(key, field="series_item_key")
    for key in args.canonical_series_key:
        validate_canonical_key(key)

    output_dir = Path(args.output_dir).resolve()
    return BootstrapRequest(
        provider_group_key=args.provider_group_key,
        source_key=args.source_key,
        module_name=module_stem,
        cadence_label=args.cadence_label,
        cron_schedule=args.cron_schedule,
        series_item_keys=args.series_item_key,
        canonical_series_keys=args.canonical_series_key,
        provider_series_ids=args.provider_series_id,
        provider_name=args.provider_name,
        ownership_mode=args.ownership_mode,
        output_dir=output_dir,
        metric_name=args.metric_name,
        dataset_description=args.dataset_description,
        dataset_geographic_scope=args.dataset_geographic_scope,
        topic_tags=[tag.strip() for tag in args.topic_tags.split(",") if tag.strip()],
    )


def build_context(request: BootstrapRequest) -> dict[str, str]:
    provider_upper = request.provider_group_key.upper()
    source_constant_name = f"{provider_upper}_{request.module_name.upper()}_KEY"
    builder_function_name = f"build_{request.module_name}_workflow"
    workflow_id = f"wf-{request.source_key}"
    topic_tags_literal = ", ".join(f'"{tag}"' for tag in request.topic_tags) or '"TODO_TOPIC"'

    series_rows = []
    for idx, (series_item, provider_series, canonical_key) in enumerate(
        zip(
            request.series_item_keys,
            request.provider_series_ids,
            request.canonical_series_keys,
            strict=False,
        ),
        start=1,
    ):
        series_rows.append(
            "    {\n"
            f"        \"series_item_key\": \"{series_item}\",\n"
            f"        \"provider_series_id\": \"{provider_series}\",\n"
            f"        \"canonical_series_key\": \"{canonical_key}\",\n"
            f"        \"metric_name\": \"{request.metric_name}_{idx}\",\n"
            f"        \"dataset_description\": \"{request.dataset_description}\",\n"
            f"        \"dataset_geographic_scope\": \"{request.dataset_geographic_scope}\",\n"
            f"        \"topic_tags\": [{topic_tags_literal}],\n"
            f"        \"frequency\": \"{request.cadence_label}\",\n"
            "    },"
        )

    return {
        "module_name": request.module_name,
        "source_constant_name": source_constant_name,
        "source_key": request.source_key,
        "provider_name": request.provider_name,
        "provider_group_key": request.provider_group_key,
        "builder_function_name": builder_function_name,
        "workflow_id": workflow_id,
        "series_configs": "\n".join(series_rows),
        "series_item_keys": ", ".join(f'"{x}"' for x in request.series_item_keys),
        "canonical_series_keys": ", ".join(f'"{x}"' for x in request.canonical_series_keys),
        "ownership_mode": request.ownership_mode,
        "cron_schedule": request.cron_schedule,
        "cadence_label": request.cadence_label,
    }


def run(request: BootstrapRequest) -> Path:
    request.output_dir.mkdir(parents=True, exist_ok=True)
    target_path = request.output_dir / f"{request.module_name}.py"

    ensure_output_path_available(target_path)
    ensure_source_key_available(request.source_key, source_dir=request.output_dir)

    rendered = render_scaffold(TEMPLATE_PATH, build_context(request))
    target_path.write_text(rendered, encoding="utf-8")
    return target_path


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    try:
        request = parse_request(argv)
        generated = run(request)
        emit_success(
            generated_file=str(generated),
            source_key=request.source_key,
            next_steps=[
                "Fill in provider-specific fetch and mapping logic",
                "Review SOURCE_SPEC metadata values",
                "Run pipeline orchestration tests",
            ],
        )
        return 0
    except FileExistsError as exc:
        emit_failure(error_code="file_exists", message=str(exc))
        return 1
    except ValueError as exc:
        emit_failure(error_code="invalid_input", message=str(exc))
        return 1
    except BootstrapError as exc:
        emit_failure(error_code=exc.code, message=exc.message)
        return 1
    except Exception as exc:  # pragma: no cover - defensive boundary
        emit_failure(error_code="generation_failed", message=str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
