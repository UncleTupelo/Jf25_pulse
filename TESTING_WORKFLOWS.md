# Testing GitHub Actions Workflows Locally

This guide explains how to test the GitHub Actions workflows locally before pushing to GitHub.

## Prerequisites

Install [act](https://github.com/nektos/act), a tool that allows you to run GitHub Actions locally:

```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Windows (with Chocolatey)
choco install act-cli
```

## Testing Individual Workflows

### Test Python CI Workflow

```bash
# Test the lint job
act -j lint -W .github/workflows/ci-python.yml

# Test the test job (specific OS)
act -j test -W .github/workflows/ci-python.yml --matrix os:ubuntu-latest --matrix python-version:3.10
```

### Test Frontend CI Workflow

```bash
# Test lint and typecheck
act -j lint-and-typecheck -W .github/workflows/ci-frontend.yml

# Test build (specific OS)
act -j build -W .github/workflows/ci-frontend.yml --matrix os:ubuntu-latest
```

### Test PR Checks Workflow

```bash
# Test pre-commit checks
act pull_request -j pre-commit -W .github/workflows/pr-checks.yml

# Test PR title check
act pull_request -j pr-title-check -W .github/workflows/pr-checks.yml
```

## Testing with Events

### Simulate Pull Request Event

```bash
# Create a mock event
cat > /tmp/pr-event.json << 'EOF'
{
  "pull_request": {
    "number": 1,
    "title": "feat: add new feature",
    "head": {
      "ref": "feature-branch",
      "sha": "abc123"
    },
    "base": {
      "ref": "main"
    }
  }
}
EOF

# Run with the event
act pull_request -e /tmp/pr-event.json
```

### Simulate Push Event

```bash
act push -W .github/workflows/ci-python.yml
```

## Running Pre-commit Locally

Instead of testing the entire workflow, you can run pre-commit hooks directly:

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run isort --all-files
```

## Testing Python Components

```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Run linting
black --check .
isort --check-only .

# Run tests
python test_agent_lightning_client.py
```

## Testing Frontend Components

```bash
cd frontend

# Install dependencies
pnpm install

# Run linting
pnpm run lint

# Run type checking
pnpm run typecheck

# Check formatting
pnpm run format -- --check

# Build
pnpm run build
```

## Common Issues

### Docker Not Found

`act` requires Docker to be installed and running:

```bash
# Check if Docker is running
docker ps

# Start Docker Desktop (macOS/Windows)
# or start Docker daemon (Linux)
sudo systemctl start docker
```

### Secrets Required

Some workflows may require secrets. You can provide them via:

```bash
# Create a .secrets file
echo "GITHUB_TOKEN=ghp_..." > .secrets

# Run with secrets
act -s GITHUB_TOKEN
```

### Large Docker Images

`act` downloads Docker images. To use a smaller image:

```bash
# Use medium-sized image
act -P ubuntu-latest=catthehacker/ubuntu:act-latest

# Use minimal image
act -P ubuntu-latest=node:16-buster-slim
```

## Dry Run

To see what would run without actually running it:

```bash
# List all jobs
act -l

# List workflows that would run on push
act push -l

# List workflows that would run on PR
act pull_request -l
```

## Tips

1. **Start Small**: Test individual jobs before testing entire workflows
2. **Use Dry Runs**: Use `-n` or `--dryrun` to see what would execute
3. **Check Logs**: Use `-v` for verbose output to debug issues
4. **Platform-Specific**: Some workflows may only work on specific OS, test accordingly
5. **Resource Usage**: Running full matrix tests locally can be resource-intensive

## Workflow Validation

GitHub provides a workflow validation tool:

```bash
# Install GitHub CLI
brew install gh  # macOS
# or
sudo apt install gh  # Linux

# Validate workflow syntax
gh workflow view ci-python.yml
```

## Further Reading

- [act documentation](https://github.com/nektos/act)
- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [Workflow syntax reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
