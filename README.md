# dm-orbit-gov-action

Reusable **composite** GitHub Action (Python) for **Orbit AI Governance** evidence collection.

**Repository:** https://github.com/deepmodel-ai/dm-orbit-gov-action

## What it does

1. Calls hosted **dm-orbit-mcp** `health` (connectivity check).
2. Collects **changed files** for the PR/push (capped; never uploads the full repo).
3. Calls MCP `validate_changed_files` with that structured payload.
4. **Orbit API** (via MCP) loads customer controls and runs LLM validation — not this Action.
5. Fails the job when any **Required** control has `passed=false` (default).

No Docker image. No binary Action distribution. Composite Action + Python source only.

## Install in an agent repo

Repo secrets:

| Secret | Purpose |
|--------|---------|
| `ORBIT_GOVERNANCE_KEY` | Bearer key forwarded to Orbit via MCP |

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
          orbit_governance_key: ${{ secrets.ORBIT_GOVERNANCE_KEY }}
```

Pin the Action to a release tag (create `v0.1.0` after you publish). Do not use `@master` in customer workflows.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `orbit_governance_key` | yes | — | Orbit governance Bearer key |
| `fail_on_required` | no | `true` | Fail job if any Required control fails |
| `source` | no | `ci` | `ci` or `local` |

**Not customer inputs:** Orbit API base URL, MCP URL, AI gateway URL/key/model.

## Outputs

| Output | Description |
|--------|-------------|
| `controls_evaluated` | Number of controls evaluated |
| `required_failed` | Number of Required controls that failed |
| `tier` | Tier returned by Orbit |
| `results` | JSON array of per-control results |
| `raw_llm_output` | Raw LLM JSON from Orbit |

## Local smoke test

```bash
python -m pip install -e ".[dev]"
# PowerShell:
#   $env:ORBIT_GOVERNANCE_KEY="your-key"
# bash:
#   export ORBIT_GOVERNANCE_KEY=your-key
python scripts/run_local_action_test.py
```

## Layout

```text
action.yml
src/dm_orbit_gov_action/
  config.py          # hardcoded ORBIT_MCP_URL
  inputs.py
  models.py
  mcp_client.py
  changed_files.py
  runner.py
  github_io.py
fixtures/sample_agent/   # local smoke fixtures
scripts/run_local_action_test.py
tests/
```

## Development

```bash
python -m pip install -e ".[dev]"
pytest -q
```
