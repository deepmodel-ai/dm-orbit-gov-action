"""Orchestrate changed-file collection → MCP validate_changed_files."""

from __future__ import annotations

import json
import os
from typing import Any

from dm_orbit_gov_action.changed_files import collect_changed_files
from dm_orbit_gov_action.github_io import info, set_failed, set_output
from dm_orbit_gov_action.inputs import read_run_options
from dm_orbit_gov_action.mcp_client import OrbitMcpClient


def log_failed_controls(results: list[dict[str, Any]]) -> None:
    failed = [row for row in results if isinstance(row, dict) and row.get("passed") is False]
    if not failed:
        return
    info(f"Failed controls ({len(failed)}):")
    for row in failed:
        key = row.get("control_key") or "?"
        findings = row.get("findings") or []
        messages = []
        for finding in findings:
            if isinstance(finding, dict) and finding.get("message"):
                messages.append(str(finding["message"]))
        detail = "; ".join(messages) if messages else "(no findings)"
        info(f"  - {key}: {detail}")


def run() -> None:
    options = read_run_options()
    info(f"Orbit MCP URL: {options.orbit_mcp_url}")
    info(f"Evidence source={options.source}")

    with OrbitMcpClient(
        mcp_url=options.orbit_mcp_url,
        scanner_token=options.orbit_scanner_token,
    ) as mcp:
        info("Calling MCP health…")
        health = mcp.call_tool("health", {})
        info(f"MCP health status={health.get('status')}")

        workspace = os.environ.get("GITHUB_WORKSPACE") or os.getcwd()
        changed = collect_changed_files(
            workspace=workspace,
            event_name=os.environ.get("GITHUB_EVENT_NAME") or "",
            event_path=os.environ.get("GITHUB_EVENT_PATH"),
            commit_sha=options.commit_sha,
        )
        truncated_note = " (truncated)" if changed.truncated else ""
        info(
            f"Changed files={len(changed.files)} "
            f"range={changed.base_ref or '(none)'}..{changed.head_ref}{truncated_note}"
        )

        tool_arguments: dict[str, Any] = {
            "source": options.source,
            "truncated": changed.truncated,
            "agent_spec_identifier": options.agent_spec_identifier,
            "target_role": options.target_role,
            "files": [
                {
                    "path": file.path,
                    "content": file.content,
                    "truncated": file.truncated,
                }
                for file in changed.files
            ],
        }
        for key, value in (
            ("commit_sha", options.commit_sha or None),
            ("scan_id", options.scan_id),
            ("base_ref", changed.base_ref or None),
            ("head_ref", changed.head_ref or None),
            ("repository", options.repository),
            ("run_url", options.run_url),
        ):
            if value is not None and value != "":
                tool_arguments[key] = value

        info("Submitting changed files via MCP validate_changed_files…")
        result = mcp.call_tool("validate_changed_files", tool_arguments)

        controls_evaluated = int(result.get("controls_evaluated") or 0)
        required_failed = int(result.get("required_failed") or 0)
        tier = str(result.get("tier_key") or result.get("tier") or "")
        results = result.get("results") if isinstance(result.get("results"), list) else []
        raw_llm_output = result.get("raw_llm_output")

        set_output("controls_evaluated", str(controls_evaluated))
        set_output("required_failed", str(required_failed))
        set_output("tier", tier)
        set_output("raw_llm_output", json.dumps(raw_llm_output, default=str))
        set_output("results", json.dumps(results, default=str))

        log_failed_controls(results)
        ok = result.get("ok")
        info(
            f"Done. ok={ok} controls_evaluated={controls_evaluated} "
            f"required_failed={required_failed} tier={tier}"
        )

        if options.fail_on_required and (required_failed > 0 or ok is False):
            set_failed(
                f"{required_failed} Required control(s) failed evidence checks "
                "(see Action logs / raw_llm_output for details)"
            )
