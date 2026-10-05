"""CLI entrypoint for the composite GitHub Action."""

from __future__ import annotations

from dm_orbit_gov_action.github_io import set_failed
from dm_orbit_gov_action.runner import run


def main() -> None:
    try:
        run()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — surface any failure to Actions
        set_failed(str(exc))


if __name__ == "__main__":
    main()
