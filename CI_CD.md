# CI/CD Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) workflows used in this project.

## Overview

The project uses GitHub Actions for automated testing, quality checks, security scanning, and releases.

## Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Pull requests to `main` or `develop` branches
- Direct pushes to `main` or `develop` branches

**Jobs:**

#### Backend Checks
- **backend-lint**: Runs code formatting checks with `black` and `isort`
- **backend-typecheck**: Performs static type checking with `mypy`
- **backend-tests**: Runs existing Python test files

#### Frontend Checks
- **frontend-lint**: Runs ESLint and Prettier checks
- **frontend-typecheck**: Performs TypeScript type checking

#### Build Verification
- **build-backend**: Verifies that the backend can be built successfully

**Purpose:** Ensure code quality and catch issues early before merging.

### 2. CodeQL Security Scan (`.github/workflows/codeql.yml`)

**Triggers:**
- Pushes to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Scheduled weekly scan (Mondays at midnight)

**Languages Analyzed:**
- JavaScript/TypeScript
- Python

**Purpose:** Automatically detect security vulnerabilities and code quality issues.

### 3. Release Workflow (`.github/workflows/release.yml`)

**Triggers:**
- Manual workflow dispatch with version tag input
- Push of version tags (e.g., `v1.0.0`)

**Platforms Built:**
- macOS (latest)
- Windows (latest)
- Linux (Ubuntu latest)

**Features:**
- Automated version bumping in `package.json`
- Multi-platform builds (Mac, Windows, Linux)
- Backend compilation with PyInstaller
- Frontend compilation with Electron Builder
- **SHA256 checksum generation** for all artifacts
- **Automated release notes** with download instructions
- Draft release creation for review before publishing

**Artifacts Generated:**
- `.dmg` (macOS installer)
- `.exe` (Windows installer)
- `.AppImage`, `.deb`, `.rpm` (Linux packages)
- Auto-update metadata files
- Checksum files for verification

### 4. PR Labeler (`.github/workflows/labeler.yml`)

**Triggers:**
- Pull request opened, edited, or synchronized

**Purpose:** Automatically label PRs based on the files changed:
- `frontend` - Changes to frontend code
- `backend` - Changes to backend code
- `documentation` - Changes to documentation
- `ci-cd` - Changes to CI/CD workflows
- `configuration` - Changes to config files
- `dependencies` - Dependency updates
- `tests` - Changes to test files
- `build` - Changes to build scripts

### 5. Stale Issues/PRs (`.github/workflows/stale.yml`)

**Triggers:**
- Daily at midnight
- Manual workflow dispatch

**Behavior:**
- **Issues:** Marked stale after 60 days of inactivity, closed 7 days later
- **Pull Requests:** Marked stale after 45 days of inactivity, closed 14 days later

**Exemptions:**
- Issues/PRs labeled: `pinned`, `security`, `roadmap`, `help wanted`, `in-progress`

## Dependabot Configuration (`.github/dependabot.yml`)

**Update Schedule:** Weekly on Mondays

**Monitored Dependencies:**
1. **Python (pip)**: Backend dependencies in `pyproject.toml`
2. **npm**: Frontend dependencies in `frontend/package.json`
3. **GitHub Actions**: Action versions in workflow files

**Configuration:**
- Automatic PR creation for dependency updates
- Groups updates by ecosystem
- Limits number of open PRs to prevent spam
- Ignores major version updates for critical packages (Electron, React)

## Pre-commit Hooks (`.pre-commit-config.yaml`)

Automatically formats code before commit:
- **Black**: Python code formatting
- **isort**: Python import sorting
- **Frontend lint**: TypeScript/JavaScript type checking

**Setup:**
```bash
pip install pre-commit
pre-commit install
```

## Status Badges

Add these badges to your README to show build status:

```markdown
[![CI](https://github.com/UncleTupelo/Jf25_pulse/workflows/CI/badge.svg)](https://github.com/UncleTupelo/Jf25_pulse/actions/workflows/ci.yml)
[![CodeQL](https://github.com/UncleTupelo/Jf25_pulse/workflows/CodeQL%20Security%20Scan/badge.svg)](https://github.com/UncleTupelo/Jf25_pulse/actions/workflows/codeql.yml)
[![Release](https://github.com/UncleTupelo/Jf25_pulse/workflows/Release/badge.svg)](https://github.com/UncleTupelo/Jf25_pulse/actions/workflows/release.yml)
```

## Best Practices

### For Contributors

1. **Before submitting a PR:**
   - Ensure all CI checks pass locally
   - Run `pre-commit run --all-files` to format code
   - Run `pnpm run typecheck` in frontend directory
   - Run `black opencontext && isort opencontext` for backend

2. **PR Requirements:**
   - All CI checks must pass
   - At least one approval required
   - No merge conflicts
   - Follows branch naming convention

3. **Security:**
   - Address CodeQL findings before merging
   - Review Dependabot PRs promptly
   - Never commit secrets or credentials

### For Maintainers

1. **Release Process:**
   - Create a version tag: `git tag v1.0.0`
   - Push tag: `git push origin v1.0.0`
   - GitHub Actions builds all platforms automatically
   - Review draft release and publish when ready

2. **Managing Stale Items:**
   - Review stale issues/PRs weekly
   - Remove `stale` label to keep items open
   - Add `pinned` label for important items

3. **Dependency Updates:**
   - Review and test Dependabot PRs
   - Merge in batches to minimize disruption
   - Check for breaking changes in changelogs

## Troubleshooting

### CI Failures

**Backend lint failures:**
```bash
# Fix formatting issues
black opencontext
isort opencontext
```

**Frontend lint failures:**
```bash
cd frontend
pnpm run lint --fix
pnpm exec prettier --write .
```

**Type check failures:**
```bash
# Backend
mypy opencontext --ignore-missing-imports

# Frontend
cd frontend
pnpm run typecheck
```

### Build Failures

**Backend build:**
```bash
# Clean and rebuild
rm -rf dist build
uv sync
source .venv/bin/activate
./build.sh
```

**Frontend build:**
```bash
cd frontend
rm -rf dist out
pnpm install
pnpm run build
```

### Release Issues

**Failed release:**
1. Check GitHub Actions logs for specific error
2. Verify secrets are configured (CSC_LINK, APPLE_ID, etc.)
3. Ensure tag format is correct (v*.*.*)
4. Delete failed draft release and re-run

## Secrets Required

For releases to work, configure these repository secrets:

### macOS Code Signing
- `CSC_LINK`: Base64-encoded certificate
- `CSC_KEY_PASSWORD`: Certificate password
- `APPLE_ID`: Apple ID email
- `APPLE_APP_SPECIFIC_PASSWORD`: App-specific password
- `APPLE_TEAM_ID`: Apple Developer Team ID

### GitHub
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

## Monitoring

- **CI Status**: Check [Actions tab](https://github.com/UncleTupelo/Jf25_pulse/actions)
- **Security Alerts**: Check [Security tab](https://github.com/UncleTupelo/Jf25_pulse/security)
- **Dependency Updates**: Check [Dependabot PRs](https://github.com/UncleTupelo/Jf25_pulse/pulls)

## Future Enhancements

Potential improvements to consider:

- [ ] Add test coverage reporting
- [ ] Add performance benchmarking
- [ ] Implement semantic versioning automation
- [ ] Add Docker image builds
- [ ] Set up artifact registry
- [ ] Add automatic changelog generation from commits
- [ ] Implement canary/beta release channels
- [ ] Add automated smoke tests for releases
