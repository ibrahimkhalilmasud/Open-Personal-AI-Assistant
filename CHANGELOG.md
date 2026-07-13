# CHANGELOG

## Purpose
Track release-level changes.

## Audience
Users and contributors.

## Prerequisites
None.

## Step-by-step
Review sections by version.

## 1.0.0 - 2026-07-13
### Added
- Full documentation set for installation, operation, architecture, API, SDK, memory, tools, agents, plugins, admin, troubleshooting, FAQ, roadmap.
- Version 1.0 release assets guidance.

### Verified
- CLI command matrix from `main.py`.
- REST API endpoint matrix from `app/api/server.py` and `app/api/routes/*`.
- Installer scripts (`installers/*`), Docker (`Dockerfile`, `docker-compose.yml`), launcher (`launcher.py`).
- Test suite: `python -m unittest discover -s tests -q`.

### Notes
- Commands such as `--setup`, `--backup`, `--restore`, `--demo`, `--plugin-list`, `--tool-list` are not currently implemented.

## Examples
Use this file to generate GitHub release notes.

## Troubleshooting
If release notes mismatch behavior, regenerate from current `main.py --help` and route files.

## Related documents
- [README.md](README.md)
- [ROADMAP.md](ROADMAP.md)
