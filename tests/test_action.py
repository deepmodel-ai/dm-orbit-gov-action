"""Unit tests for Orbit governance Action helpers."""

from __future__ import annotations

import pytest

from dm_orbit_gov_action.changed_files import is_likely_text_path
from dm_orbit_gov_action.config import ORBIT_MCP_URL
from dm_orbit_gov_action.inputs import read_run_options
from dm_orbit_gov_action.mcp_client import extract_tool_object, parse_sse_json_payloads


def test_orbit_mcp_url_is_hardcoded() -> None:
    assert ORBIT_MCP_URL == "https://dm-orbit-mcp-444791763526.us-central1.run.app/mcp"


def test_is_likely_text_path() -> None:
    assert is_likely_text_path("src/agent.py") is True
    assert is_likely_text_path("logo.png") is False


def test_parse_sse_json_payloads() -> None:
    payloads = parse_sse_json_payloads('data: {"id": 1, "result": {"ok": true}}\n\n')
    assert payloads[0]["id"] == 1


def test_extract_tool_object_from_text_content() -> None:
    result = extract_tool_object(
        {"content": [{"type": "text", "text": '{"status": "ok"}'}]}
    )
    assert result["status"] == "ok"


def test_read_run_options_requires_scanner_token(monkeypatch) -> None:
    monkeypatch.delenv("INPUT_ORBIT_SCANNER_TOKEN", raising=False)
    monkeypatch.setenv("INPUT_AGENT_SPEC_IDENTIFIER", "20ac6463-fbe5-4136-9c6e-e02a1bdb515b")
    monkeypatch.setenv("GITHUB_SHA", "abc")
    with pytest.raises(ValueError, match="ORBIT_SCANNER_TOKEN"):
        read_run_options()


def test_read_run_options_requires_identifier(monkeypatch) -> None:
    monkeypatch.setenv("INPUT_ORBIT_SCANNER_TOKEN", "orb_sc_test")
    monkeypatch.delenv("INPUT_AGENT_SPEC_IDENTIFIER", raising=False)
    monkeypatch.setenv("GITHUB_SHA", "abc")
    with pytest.raises(ValueError, match="agent_spec_identifier"):
        read_run_options()

