# dm-orbit-gov-action

Reusable **composite** GitHub Action (Python) for **Orbit AI Governance** evidence collection.

**Repository:** https://github.com/deepmodel-ai/dm-orbit-gov-action

## What it does

1. Calls hosted **dm-orbit-mcp** `health` (auth + connectivity).
2. Collects **changed files** for the PR/push (capped; never uploads the full repo).
3. Calls MCP `validate_changed_files` with that payload.
4. **Orbit API** (via MCP) loads applicable controls, runs LLM evaluation, and writes scanner evidence.
5. Fails the job when any **Required** control has `passed=false` (default).

## Install in an agent repo

Repo secret: `ORBIT_SCANNER_TOKEN` (`orb_sc_…` from Orbit Admin → scanner credentials).

```yaml
name: Orbit governance evidence

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  evidence:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Orbit governance scan
        uses: deepmodel-ai/dm-orbit-gov-action@v0.1.0
        with:
          orbit_scanner_token: ${{ secrets.ORBIT_SCANNER_TOKEN }}
          agent_spec_identifier: ${{ vars.ORBIT_AGENT_SPEC_IDENTIFIER }}
          target_role: CANDIDATE
```

Pin to a release tag. Do not use `@master` in customer workflows.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `orbit_scanner_token` | yes | — | Opaque `orb_sc_…` scanner credential |
| `agent_spec_identifier` | one of* | — | Capability UUID (with `target_role`) |
| `target_role` | with identifier | `CANDIDATE` | `CANDIDATE` or `PRODUCTION` |
| `agent_spec_id` | one of* | — | Pinned AgentSpec version UUID |
| `repository` | no | from `GITHUB_REPOSITORY` | Canonical `github:owner/repo` if credential is repo-scoped |
| `fail_on_required` | no | `true` | Fail job if Required controls fail |
| `source` | no | `ci` | `ci` or `local` |

\* Exactly one targeting form: identifier+role **or** `agent_spec_id`.

**Not customer inputs:** Orbit API base URL, MCP URL, AI gateway secrets.

## Outputs

| Output | Description |
|--------|-------------|
| `controls_evaluated` | Number of controls evaluated |
| `required_failed` | Number of Required controls that failed |
| `tier` | Tier key returned by Orbit |
| `results` | JSON array of per-control results |
| `raw_llm_output` | Raw LLM JSON from Orbit |

## Local smoke test

```bash
python -m pip install -e ".[dev]"
cp .env.example .env   # fill ORBIT_SCANNER_TOKEN + targeting
# load .env into the shell, then:
python scripts/run_local_action_test.py
```

## Failure behavior

| Case | Result |
|------|--------|
| Missing / invalid `orb_sc_` | Job fails (401 from Orbit via MCP) |
| Missing agent_spec targeting | Job fails at input validation |
| MCP / Orbit HTTP / timeout | Job fails with error annotation |
| Required control `passed=false` | Job fails when `fail_on_required=true` |
| Recommended-only failures | Job succeeds (outputs still list findings) |
