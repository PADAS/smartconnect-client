# smartconnect-client
Python client for using SMART Connect API

This is initially mean to satisfy essentials for adapting Gundi to push EarthRanger Reports to SMART Connect.

## Development

Uses [uv](https://docs.astral.sh/uv/) with a [hatchling](https://hatch.pypa.io/) build backend.

```
uv sync          # create .venv and install dependencies (incl. dev group)
uv run pytest    # run the test suite
uv build         # build wheel + sdist into dist/
```

## Release

Push a `v*.*.*` tag matching the version in `pyproject.toml`. The release
workflow runs the test suite, builds, publishes to PyPI via Trusted
Publishing (OIDC), and attaches the artifacts to a GitHub Release.
