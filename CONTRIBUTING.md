# CONTRIBUTING

## Purpose
Guide contributors on safe, reviewable contributions.

## Audience
Open-source contributors.

## Prerequisites
Fork, branch, local test environment.

## Step-by-step
1. Fork repository.
2. Create feature branch.
3. Keep changes focused.
4. Run tests:
   ```bash
   python -m unittest discover -s tests -q
   ```
5. Update docs for behavior changes.
6. Open PR with clear summary and validation evidence.

## Examples
- Good PR: single feature + tests + docs updates.
- Bad PR: unrelated refactors mixed with feature work.

## Troubleshooting
If tests fail locally, include failure logs and environment details in PR.

## Related documents
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- [SECURITY.md](SECURITY.md)
- [CHANGELOG.md](CHANGELOG.md)
