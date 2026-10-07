# PR Notes — DM-2239 / v0.2.0

---

## 1) Feature PR → `staging`

**Branch:** `feature-dm-2239-scanner-evaluate-bridge` → `staging`  
**Title:** `Feature | DM-2239 Wire Action to scanner token and AgentSpec targeting`

```md
## Title

Wire Action to scanner token and AgentSpec targeting

https://deepmodel.atlassian.net/browse/DM-2239

## Type of Change

- [x] New feature
- [ ] Bug fix
- [ ] Refactoring
- [ ] Security patch

## Description

Align `dm-orbit-gov-action` with the Orbit scanner evaluate-changes contract. Customer workflows authenticate with an opaque `orb_sc_…` scanner credential and target a capability via `agent_spec_identifier` + `target_role` (`CANDIDATE` | `PRODUCTION`).

Replaces the previous `orbit_governance_key` Bearer input. The Action still collects capped changed files and calls hosted dm-orbit-mcp `health` / `validate_changed_files`; Orbit API owns control lookup, LLM evaluation, and scanner evidence writes.

Package / pin version is bumped to **v0.2.0**.

## What is fixed / implemented?

- Inputs: `orbit_scanner_token`, `agent_spec_identifier`, `target_role`, optional `repository`; removed `orbit_governance_key` and `agent_spec_id`.
- MCP client uses `Authorization: Bearer <orb_sc_…>` and a longer timeout for evaluate.
- Runner always sends `agent_spec_identifier` + `target_role`, plus optional `repository` / `run_url` / commit metadata.
- Fails the job when `fail_on_required` is true and `required_failed > 0` or MCP returns `ok=false`.
- README install example pins `@v0.2.0` and documents Secrets (not Variables) for token + identifier.
- `.env.example` and local smoke script updated for the new inputs.
- Unit tests for missing scanner token / missing identifier.
- Version bump: `pyproject.toml` and `CLIENT_VERSION` → `0.2.0`.

## Additional Information

- Env changes:
  - **New:** `ORBIT_SCANNER_TOKEN`, `ORBIT_AGENT_SPEC_IDENTIFIER` (customer repo Secrets); Action inputs `INPUT_ORBIT_SCANNER_TOKEN`, `INPUT_AGENT_SPEC_IDENTIFIER`, `INPUT_TARGET_ROLE`, optional `INPUT_REPOSITORY`.
  - **Delete:** `ORBIT_GOVERNANCE_KEY` / `orbit_governance_key` / `INPUT_ORBIT_GOVERNANCE_KEY`.
  - **Change:** none renamed beyond the replacements above.
- DB migration: None.
- Infra changes: None. Calls existing hosted dm-orbit-mcp.

## Checklist

- [x] I have added or updated relevant tests to cover the changes.
- [x] I have performed a self-review of my code.
- [x] My changes generate no new warnings or errors.
- [x] Environment variables have been updated (if applicable).
- [x] Any new packages are listed in the requirements.txt (if applicable).
```

---

## 2) Release PR — merge `staging` → `master` (v0.2.0)

**Branch:** `staging` → `master`  
**Title:** `Release | DM-2239 Publish Orbit governance evidence Action v0.2.0`

```md
## Title

Publish Orbit governance evidence Action v0.2.0

https://deepmodel.atlassian.net/browse/DM-2239

## Type of Change

- [x] New feature
- [ ] Bug fix
- [ ] Refactoring
- [ ] Security patch

## Description

Merge `staging` into `master` to release **v0.2.0** of `deepmodel-ai/dm-orbit-gov-action`.

This release switches customer auth to opaque scanner tokens (`orb_sc_…`) and requires capability targeting via `agent_spec_identifier` + `target_role`. It is a **breaking change** for any consumer still on `@v0.1.0` with `orbit_governance_key`.

After merge, create and push the `v0.2.0` git tag on `master` so consumers can pin:

```yaml
uses: deepmodel-ai/dm-orbit-gov-action@v0.2.0
with:
  orbit_scanner_token: ${{ secrets.ORBIT_SCANNER_TOKEN }}
  agent_spec_identifier: ${{ secrets.ORBIT_AGENT_SPEC_IDENTIFIER }}
  target_role: CANDIDATE
```

## What is fixed / implemented?

- Scanner-token auth + AgentSpec identifier/role targeting end to end in the composite Action.
- Breaking input rename: `orbit_governance_key` → `orbit_scanner_token`.
- Docs, local smoke, and unit tests updated for the new contract.
- Package version `0.2.0`.

## Additional Information

- Env changes:
  - **New:** `ORBIT_SCANNER_TOKEN`, `ORBIT_AGENT_SPEC_IDENTIFIER`.
  - **Delete:** `ORBIT_GOVERNANCE_KEY`.
  - **Change:** none beyond the replacements above.
- DB migration: None.
- Infra changes: None. Tag + Action source only.

## Checklist

- [x] I have added or updated relevant tests to cover the changes.
- [x] I have performed a self-review of my code.
- [x] My changes generate no new warnings or errors.
- [x] Environment variables have been updated (if applicable).
- [x] Any new packages are listed in the requirements.txt (if applicable).
```

---

## 3) Release tag note — `v0.2.0`

**Tag:** `v0.2.0` (on `master` after the release PR merges)  
**GitHub Release title:** `v0.2.0 — Scanner token + AgentSpec targeting`

```md
## v0.2.0 — Scanner token + AgentSpec targeting

Aligns the Orbit governance evidence Action with the scanner evaluate-changes contract.

**Ticket:** https://deepmodel.atlassian.net/browse/DM-2239  
**Repo:** https://github.com/deepmodel-ai/dm-orbit-gov-action

### Breaking changes

- `orbit_governance_key` removed → use `orbit_scanner_token` (`orb_sc_…`).
- `agent_spec_identifier` is required; pair with `target_role` (`CANDIDATE` | `PRODUCTION`).
- `agent_spec_id` is not supported on this Action.

### Install

```yaml
uses: deepmodel-ai/dm-orbit-gov-action@v0.2.0
with:
  orbit_scanner_token: ${{ secrets.ORBIT_SCANNER_TOKEN }}
  agent_spec_identifier: ${{ secrets.ORBIT_AGENT_SPEC_IDENTIFIER }}
  target_role: CANDIDATE
```

Store both values under **Secrets** (not Variables).

### Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `orbit_scanner_token` | yes | — | Opaque `orb_sc_…` |
| `agent_spec_identifier` | yes | — | Capability UUID |
| `target_role` | no | `CANDIDATE` | `CANDIDATE` or `PRODUCTION` |
| `repository` | no | from `GITHUB_REPOSITORY` | `github:owner/repo` if credential is repo-scoped |
| `fail_on_required` | no | `true` | Fail job if Required controls fail |
| `source` | no | `ci` | `ci` or `local` |

### Additional Information

- Env changes: New `ORBIT_SCANNER_TOKEN` + `ORBIT_AGENT_SPEC_IDENTIFIER`; delete `ORBIT_GOVERNANCE_KEY`.
- DB migration: None.
- Infra changes: None.

### How to tag (after master merge)

```bash
git checkout master
git pull origin master
git tag -a v0.2.0 -m "v0.2.0 — Scanner token + AgentSpec targeting"
git push origin v0.2.0
```
```
