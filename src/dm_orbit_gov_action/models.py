"""Typed models for the governance Action run."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RunOptions(BaseModel):
    model_config = ConfigDict(frozen=True)

    orbit_mcp_url: str
    orbit_scanner_token: str
    fail_on_required: bool
    source: str
    commit_sha: str
    scan_id: str | None = None
    agent_spec_identifier: str | None = None
    target_role: str | None = None
    agent_spec_id: str | None = None
    repository: str | None = None
    run_url: str | None = None


class ChangedFile(BaseModel):
    model_config = ConfigDict(frozen=True)

    path: str
    content: str
    truncated: bool = False


class ChangedFilesResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    base_ref: str
    head_ref: str
    files: list[ChangedFile]
    truncated: bool = False
