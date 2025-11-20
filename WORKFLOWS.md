# GitHub Actions Workflows

This document describes the GitHub Actions workflows configured for this project.

## Continuous Integration (CI)

### Python CI (`ci-python.yml`)

Runs on: Push to `main`/`develop` branches and Pull Requests

**Jobs:**
- **Lint**: Checks code formatting with `black` and import sorting with `isort`
- **Test**: Runs Python tests across multiple OS (Ubuntu, Windows, macOS) and Python versions (3.10, 3.11, 3.12)

**Triggered by changes to:**
- Python files (`*.py`)
- `pyproject.toml`
- The workflow file itself

### Frontend CI (`ci-frontend.yml`)

Runs on: Push to `main`/`develop` branches and Pull Requests

**Jobs:**
- **Lint and Type Check**: Runs ESLint, TypeScript type checking, and Prettier format checking
- **Build**: Builds the backend and frontend across multiple OS (Ubuntu, Windows, macOS)

**Triggered by changes to:**
- Files in `frontend/` directory
- The workflow file itself

## Pull Request Checks

### PR Checks (`pr-checks.yml`)

Runs on: All Pull Requests

**Jobs:**
- **PR Title Check**: Validates PR titles follow conventional commit format (feat, fix, docs, etc.)
- **PR Size Check**: Warns if a PR changes more than 50 files
- **Pre-commit**: Runs all pre-commit hooks to ensure code quality

### PR Labeler (`labeler.yml`)

Runs on: Pull Request open/update

**Jobs:**
- Automatically labels PRs based on changed files:
  - `frontend`: Changes to frontend code
  - `backend`: Changes to Python/backend code
  - `documentation`: Changes to markdown/docs
  - `config`: Changes to configuration files
  - `tests`: Changes to test files
  - `workflows`: Changes to GitHub Actions
  - `dependencies`: Changes to dependencies

## Security

### CodeQL Analysis (`codeql-analysis.yml`)

Runs on: 
- Push to `main`/`develop` branches
- Pull Requests
- Weekly schedule (Monday 2:00 AM UTC)

**Jobs:**
- Analyzes Python and JavaScript code for security vulnerabilities
- Uses extended security queries for thorough analysis

## Maintenance

### Stale Issues and PRs (`stale.yml`)

Runs on: Daily at 1:00 AM UTC

**Configuration:**
- **Issues**: Marked stale after 60 days, closed after 7 more days
- **PRs**: Marked stale after 30 days, closed after 14 more days
- Exemptions: `pinned`, `security`, `bug`, `enhancement`, `work-in-progress` labels

### Dependabot

Configuration in `.github/dependabot.yml`

**Updates:**
- **Python dependencies**: Weekly on Mondays
- **NPM dependencies**: Weekly on Mondays  
- **GitHub Actions**: Weekly on Mondays

All dependency updates are automatically labeled with `dependencies` and their ecosystem label.

## Community

### First Time Contributors (`greetings.yml`)

Runs on: First issue or PR from a contributor

**Jobs:**
- Welcomes first-time issue creators
- Welcomes first-time PR contributors with a checklist

## Release

### Release Workflow (`release.yml`)

Runs on:
- Manual trigger with version tag input
- Push of version tags (v*.*.*)

**Jobs:**
- Builds application for macOS, Windows, and Linux
- Creates draft GitHub releases with artifacts
- Handles code signing for macOS and Windows

## Local Development

### Running Workflows Locally

You can test workflows locally using [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# Run a specific workflow
act -j lint  # Run the lint job
act pull_request  # Run all PR workflows

# Run with secrets
act -s GITHUB_TOKEN=your_token
```

### Pre-commit Hooks

Install pre-commit hooks locally:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

## Workflow Status Badges

Add these to your README.md to show workflow status:

```markdown
![Python CI](https://github.com/UncleTupelo/Jf25_pulse/workflows/Python%20CI/badge.svg)
![Frontend CI](https://github.com/UncleTupelo/Jf25_pulse/workflows/Frontend%20CI/badge.svg)
![CodeQL](https://github.com/UncleTupelo/Jf25_pulse/workflows/CodeQL%20Security%20Analysis/badge.svg)
```

## Best Practices

### For Contributors

1. **Before opening a PR:**
   - Run pre-commit hooks: `pre-commit run --all-files`
   - Test locally: Run relevant tests for your changes
   - Follow conventional commit format for PR title

2. **PR Guidelines:**
   - Keep PRs focused and small (< 50 files when possible)
   - Update documentation for user-facing changes
   - Add tests for new features

3. **Responding to CI Failures:**
   - Check the Actions tab for detailed logs
   - Fix linting issues: `black .` and `isort .`
   - Fix type errors: Check TypeScript errors
   - Re-run failed jobs after pushing fixes

### For Maintainers

1. **Review Dependabot PRs:**
   - Check for breaking changes
   - Test locally before merging
   - Batch non-breaking updates

2. **Security Alerts:**
   - CodeQL runs weekly and on all PRs
   - Review and address security alerts promptly
   - Use `security` label to prevent auto-closure

3. **Stale Management:**
   - Review stale items before auto-closure
   - Use `pinned` label for important issues
   - Close obsolete issues manually with explanation

## Troubleshooting

### Common Issues

**Pre-commit hook fails on CI but passes locally:**
- Ensure you've committed `.pre-commit-config.yaml`
- Update hooks: `pre-commit autoupdate`

**Build fails on specific OS:**
- Check platform-specific dependencies
- Review build logs in Actions tab
- Test locally with Docker or VM

**Dependabot PRs fail:**
- May indicate breaking changes
- Review changelog of updated packages
- Update code to handle breaking changes

**CodeQL warnings:**
- Review security implications
- Fix legitimate issues
- Mark false positives with inline comments
