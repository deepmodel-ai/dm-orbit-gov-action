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

### 1. Create repository secrets

Settings → Secrets and variables → Actions → **Secrets** (not Variables):

| Secret | Value |
|--------|--------|
| `ORBIT_SCANNER_TOKEN` | Opaque `orb_sc_…` from Orbit Admin → scanner credentials |
| `ORBIT_AGENT_SPEC_IDENTIFIER` | Capability UUID (`agent_spec_identifier`) |

`secrets.*` and `vars.*` are different. Store values under Secrets and pass `${{ secrets.NAME }}`.

### 2. Workflow

In the **agent repo**, create `.github/workflows/orbit-governance.yml` and paste:

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
        uses: deepmodel-ai/dm-orbit-gov-action@v0.2.0
        with:
          orbit_scanner_token: ${{ secrets.ORBIT_SCANNER_TOKEN }}
          agent_spec_identifier: ${{ secrets.ORBIT_AGENT_SPEC_IDENTIFIER }}
          target_role: CANDIDATE
```

Pin to a release tag (`@v0.2.0`). Do not use `@master` or a feature branch in customer workflows.

The Action does **not** read GitHub secrets by name automatically — pass them via `with:`.

Targeting is **capability + role only** (`agent_spec_identifier` + `target_role`). There is no `agent_spec_id` input on this Action.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `orbit_scanner_token` | yes | — | Opaque `orb_sc_…` |
| `agent_spec_identifier` | yes | — | Capability UUID |
| `target_role` | no | `CANDIDATE` | `CANDIDATE` or `PRODUCTION` |
| `repository` | no | from `GITHUB_REPOSITORY` | Canonical `github:owner/repo` if credential is repo-scoped |
| `fail_on_required` | no | `true` | Fail job if Required controls fail |
| `source` | no | `ci` | `ci` or `local` |

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
cp .env.example .env   # fill ORBIT_SCANNER_TOKEN + INPUT_AGENT_SPEC_IDENTIFIER
python scripts/run_local_action_test.py
```

## Failure behavior

| Case | Result |
|------|--------|
| Missing / invalid `orb_sc_` | Job fails (401 from Orbit via MCP) |
| Empty identifier (`vars` used for a Secret) | Job fails at input validation |
| MCP / Orbit HTTP / timeout | Job fails with error annotation |
| Required control `passed=false` | Job fails when `fail_on_required=true` |
| Recommended-only failures | Job succeeds (outputs still list findings) |
