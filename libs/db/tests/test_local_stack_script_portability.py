"""Polish checks for local-stack script strictness and portability basics."""

from __future__ import annotations

from pathlib import Path
import subprocess


SCRIPTS = [
    Path("tools/quality/local-stack/test-local-db-bootstrap.sh"),
    Path("tools/quality/local-stack/run-db-migrations.sh"),
    Path("tools/quality/local-stack/check-db-revision.sh"),
    Path("tools/quality/local-stack/test-db-readiness.sh"),
]


def test_local_stack_scripts_have_strict_headers() -> None:
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert text.startswith("#!/usr/bin/env bash\nset -euo pipefail\n")


def test_local_stack_scripts_pass_bash_syntax_check() -> None:
    for script in SCRIPTS:
        subprocess.run(["bash", "-n", str(script)], check=True)
