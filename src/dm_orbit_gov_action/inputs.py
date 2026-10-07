"""Read Action inputs from INPUT_* env vars (composite wiring)."""

from __future__ import annotations

import os

from dm_orbit_gov_action.config import ORBIT_MCP_URL
from dm_orbit_gov_action.models import RunOptions


def parse_bool(raw: str, default: bool) -> bool:
    text = (raw or "").strip().lower()
    if not text:
        return default
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {raw!r}")


def read_run_options() -> RunOptions:
    orbit_scanner_token = (os.environ.get("INPUT_ORBIT_SCANNER_TOKEN") or "").strip()
    if not orbit_scanner_token:
        raise ValueError(
            "INPUT_ORBIT_SCANNER_TOKEN is required (orb_sc_…). "
            "In the workflow use: orbit_scanner_token: ${{ secrets.ORBIT_SCANNER_TOKEN }}"
        )

    fail_on_required = parse_bool(os.environ.get("INPUT_FAIL_ON_REQUIRED", "true"), True)
    source = (os.environ.get("INPUT_SOURCE") or "ci").strip().lower()
    commit_sha = (os.environ.get("GITHUB_SHA") or "").strip()
    run_id = (os.environ.get("GITHUB_RUN_ID") or "").strip()
    scan_id = f"gha-{run_id}" if run_id else None
    server_url = (os.environ.get("GITHUB_SERVER_URL") or "https://github.com").rstrip("/")
    repository = (os.environ.get("GITHUB_REPOSITORY") or "").strip()
    run_url = f"{server_url}/{repository}/actions/runs/{run_id}" if repository and run_id else None

    agent_spec_identifier = (os.environ.get("INPUT_AGENT_SPEC_IDENTIFIER") or "").strip()
    target_role = (os.environ.get("INPUT_TARGET_ROLE") or "CANDIDATE").strip().upper() or "CANDIDATE"
    repo_scope = (os.environ.get("INPUT_REPOSITORY") or "").strip() or None
    if not repo_scope and repository:
        repo_scope = f"github:{repository.lower()}"

    if source not in {"ci", "local"}:
        raise ValueError(f"Invalid source '{source}' (expected ci|local)")
    if source == "ci" and not commit_sha:
        raise ValueError("GITHUB_SHA is required when source is ci")
    if not agent_spec_identifier:
        raise ValueError(
            "agent_spec_identifier is required. "
            "Pass a Secret, e.g. agent_spec_identifier: ${{ secrets.ORBIT_AGENT_SPEC_IDENTIFIER }} "
            "(not vars.* — Secrets and Variables are different in GitHub Actions)."
        )
    if target_role not in {"CANDIDATE", "PRODUCTION"}:
        raise ValueError("INPUT_TARGET_ROLE must be CANDIDATE or PRODUCTION")

    return RunOptions(
        orbit_mcp_url=ORBIT_MCP_URL,
        orbit_scanner_token=orbit_scanner_token,
        fail_on_required=fail_on_required,
        source=source,
        commit_sha=commit_sha,
        scan_id=scan_id,
        agent_spec_identifier=agent_spec_identifier,
        target_role=target_role,
        repository=repo_scope,
        run_url=run_url,
    )
