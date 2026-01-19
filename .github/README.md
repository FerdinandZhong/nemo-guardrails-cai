# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating deployment, testing, and publishing of the NeMo Guardrails CAI package.

## Workflows

### 1. Deploy to CAI ([deploy-guardrails.yml](workflows/deploy-guardrails.yml))

**Purpose:** Automated deployment of NeMo Guardrails to Cloudera AI instances.

**Trigger:** Manual workflow dispatch

**Parameters:**
- `force_rebuild`: Force rebuild of all jobs (default: false)
- `enable_local_models`: Enable local model support with additional resources (default: false)

**Steps:**
1. **Setup Project**: Create/find CAI project and sync from GitHub
2. **Create Jobs**: Define deployment job pipeline
3. **Trigger Deployment**: Run jobs to deploy guardrails server
4. **Verify Deployment**: Test that the deployment is working

**Usage:**
```bash
# Via GitHub UI
1. Go to Actions tab
2. Select "Deploy NeMo Guardrails to CAI"
3. Click "Run workflow"
4. Select options and run

# Via GitHub CLI
gh workflow run deploy-guardrails.yml \
  -f force_rebuild=false \
  -f enable_local_models=false
```

**Required Secrets:**
- `CML_HOST`: CAI instance URL (e.g., https://ml.example.cloudera.site)
- `CML_API_KEY`: CAI API key with project creation permissions
- `GH_PAT`: GitHub Personal Access Token (for private repos)

### 2. CI - Tests and Linting ([ci.yml](workflows/ci.yml))

**Purpose:** Continuous integration for code quality and testing.

**Trigger:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**
1. **Lint**: Run Black, Ruff, and MyPy
2. **Test**: Run pytest on Python 3.9, 3.10, 3.11
3. **Build**: Build package and check with twine
4. **Docs**: Verify documentation builds

**Usage:**
Automatically runs on push/PR. No manual intervention needed.

### 3. Publish to PyPI ([publish.yml](workflows/publish.yml))

**Purpose:** Publish package to PyPI or Test PyPI.

**Trigger:**
- Automatic: When a GitHub release is published
- Manual: Workflow dispatch with version number

**Steps:**
1. Build package distributions
2. Check package validity
3. Publish to Test PyPI (manual) or PyPI (release)

**Usage:**
```bash
# Automatic (recommended)
1. Create a GitHub release
2. Package is automatically published to PyPI

# Manual (for testing)
gh workflow run publish.yml -f version=0.1.0
```

**Required Secrets:**
- `PYPI_API_TOKEN`: PyPI API token for package publishing
- `TEST_PYPI_API_TOKEN`: Test PyPI API token (optional)

## Setup Instructions

### 1. Configure Repository Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

**For CAI Deployment:**
```
CML_HOST=https://ml.example.cloudera.site
CML_API_KEY=your-cml-api-key
GH_PAT=your-github-token
```

**For PyPI Publishing:**
```
PYPI_API_TOKEN=pypi-xxxx
TEST_PYPI_API_TOKEN=pypi-xxxx (optional)
```

### 2. Enable GitHub Actions

1. Go to repository Settings → Actions → General
2. Enable "Allow all actions and reusable workflows"
3. Set "Workflow permissions" to "Read and write permissions"

### 3. Test the Workflows

#### Test CI Workflow
```bash
# Create a test branch
git checkout -b test/ci-workflow

# Make a small change
echo "# Test" >> README.md

# Push and create PR
git add .
git commit -m "test: CI workflow"
git push origin test/ci-workflow

# Create PR on GitHub
# CI workflow will run automatically
```

#### Test Deployment Workflow
```bash
# Run manually via GitHub Actions UI or CLI
gh workflow run deploy-guardrails.yml
```

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  GitHub Repository                       │
└────────────┬────────────────────────────────────────────┘
             │
             ├─► Push/PR to main/develop
             │   ↓
             │   CI Workflow (ci.yml)
             │   ├─► Lint (Black, Ruff, MyPy)
             │   ├─► Test (pytest on Py 3.9-3.11)
             │   ├─► Build (package creation)
             │   └─► Docs (documentation check)
             │
             ├─► Manual: Deploy to CAI
             │   ↓
             │   Deploy Workflow (deploy-guardrails.yml)
             │   ├─► Setup Project (create/find CAI project)
             │   ├─► Create Jobs (define deployment pipeline)
             │   ├─► Trigger Deployment (run jobs)
             │   └─► Verify Deployment (test endpoint)
             │
             └─► Release Published
                 ↓
                 Publish Workflow (publish.yml)
                 ├─► Build Package
                 ├─► Check Package
                 └─► Publish to PyPI
```

## CAI Deployment Flow

The deploy-guardrails.yml workflow orchestrates the following on your CAI instance:

```
1. Setup Project
   ├─► Create/find CML project
   ├─► Configure git sync
   └─► Set environment variables

2. Create Jobs
   ├─► Job 1: git_sync (clone repo)
   ├─► Job 2: setup_environment (install deps)
   └─► Job 3: launch_guardrails (start server)

3. Execute Jobs (Sequential)
   git_sync
      ↓
   setup_environment
      ↓
   launch_guardrails
      ↓
   ✅ Guardrails server running

4. Verify
   └─► Test endpoint health
```

## Monitoring Workflows

### View Workflow Runs

```bash
# List recent workflow runs
gh run list

# View specific run
gh run view <run-id>

# Watch a running workflow
gh run watch <run-id>

# View logs
gh run view <run-id> --log
```

### GitHub Actions UI

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Select a workflow from the left sidebar
4. View run history and logs

### Job Summaries

Each workflow creates a detailed summary with:
- Status of each job
- Project IDs (for CAI deployment)
- Error messages (if any)
- Next steps

## Troubleshooting

### Deployment Fails

**Check CAI project:**
```bash
# View project status
python -c "
from caikit import CMLClient
client = CMLClient(host='$CML_HOST', api_key='$CML_API_KEY')
projects = client.projects.list()
print([p.name for p in projects])
"
```

**Check workflow logs:**
```bash
gh run view --log
```

**Common issues:**
- API key invalid/expired → Update `CML_API_KEY` secret
- Project not found → Check `CML_HOST` configuration
- Job timeout → Increase timeout in jobs_config.yaml

### CI Fails

**Linting errors:**
```bash
# Fix locally
black nemo_guardrails_cai/ --line-length 100
ruff check nemo_guardrails_cai/ --fix
```

**Test failures:**
```bash
# Run tests locally
pytest tests/ -v
```

### Publish Fails

**Check package:**
```bash
python -m build
twine check dist/*
```

**Verify token:**
- Go to PyPI account settings
- Regenerate API token if needed
- Update `PYPI_API_TOKEN` secret

## Best Practices

1. **Use Pull Requests**: All changes should go through PR with CI checks
2. **Manual Deployment**: Use workflow dispatch for CAI deployment
3. **Test Before Release**: Test on staging environment first
4. **Version Bumping**: Update version in pyproject.toml before release
5. **Changelog**: Maintain CHANGELOG.md for releases

## Security

**Secrets Management:**
- Never commit secrets to repository
- Use GitHub Secrets for sensitive data
- Rotate API keys regularly
- Use minimal permission scopes

**Code Security:**
- Dependabot enabled for dependency updates
- CodeQL scanning (can be added)
- Security advisories for vulnerabilities

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CAI Integration Guide](../cai_integration/README.md)
- [Deployment Guide](../README.md#deploying-to-cloudera-ai-cml)

## Support

For issues with workflows:
- [GitHub Issues](https://github.com/cloudera/nemo-guardrails-cai/issues)
- Check workflow logs in Actions tab
- Review CAI project logs
