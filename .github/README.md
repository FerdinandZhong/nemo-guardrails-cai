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

## Detailed Workflow Organization

### CI Workflow Execution Model

**Trigger Events:**
- ✅ `push` to `main` or `develop` branches
- ✅ `pull_request` targeting `main` or `develop`

**Job Execution:** All jobs run **in parallel** (fastest feedback)
```
Event: Push/PR
    ↓
┌────────────────────────────────────────────┐
│ Run in parallel:                           │
│  • lint (10 min) - Black, Ruff, MyPy       │
│  • test (20 min) - Py 3.9/3.10/3.11        │
│  • build (10 min) - Package validation     │
│  • docs (10 min) - Documentation check     │
└────────────────────────────────────────────┘
    ↓
Total time: ~20 minutes (not 50!)
```

**Test Matrix Strategy:**
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
```
- Each version runs in parallel
- Catches compatibility issues
- Coverage uploaded only for 3.11

### Deploy Workflow Execution Model

**Trigger:** Manual via GitHub UI or CLI

**Parameters:**
```
force_rebuild: boolean (false)
enable_local_models: boolean (false)
```

**Job Execution:** Sequential chain with dependencies
```
Manual Trigger (GitHub Actions UI)
    ↓
1. setup-project (30 min)
   - Creates CAI project
   - Outputs: project_id
    ↓
2. create-jobs (5 min)
   - Depends on: setup-project
   - Uses: project_id from previous job
   - Reads: cai_integration/jobs_config.yaml
    ↓
3. trigger-deployment (90 min)
   - Depends on: setup-project, create-jobs
   - Passes: force_rebuild, enable_local_models flags
   - Waits for CAI jobs to complete
    ↓
4. verify-deployment (15 min)
   - Depends on: trigger-deployment
   - Only runs if: trigger-deployment succeeded
   - Reads: guardrails_info.json
    ↓
Total time: ~140 minutes
```

**Output Data Flow:**
```yaml
setup-project:
  outputs:
    project_id: ${{ steps.setup.outputs.project_id }}

create-jobs:
  needs: setup-project
  steps:
    - uses: project_id from setup-project
      run: create_jobs.py --project-id ${{ needs.setup-project.outputs.project_id }}
```

### Publish Workflow Execution Model

**Trigger Options:**

Option 1: Automatic (Release)
```
1. Create GitHub Release
    ↓
2. GitHub detects: release.types = [published]
    ↓
3. Automatically runs publish.yml
    ↓
4. Publishes to official PyPI
```

Option 2: Manual (Test PyPI)
```
GitHub UI → Actions → Publish to PyPI → Run workflow
    ↓
Input: version = "0.1.0-beta"
    ↓
Conditional: if github.event_name == 'workflow_dispatch'
    ↓
Updates pyproject.toml version
    ↓
Publishes to Test PyPI
```

**Conditional Publishing Logic:**
```yaml
# This step ONLY runs on manual trigger
- name: Publish to Test PyPI
  if: github.event_name == 'workflow_dispatch'
  run: twine upload --repository testpypi dist/*

# This step ONLY runs on release
- name: Publish to PyPI
  if: github.event_name == 'release'
  run: twine upload dist/*
```

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  GitHub Repository                       │
└────────────┬────────────────────────────────────────────┘
             │
             ├─► Push/PR to main/develop
             │   ↓
             │   CI Workflow (ci.yml) - AUTOMATIC
             │   ├─► Lint (10 min) ────┐
             │   ├─► Test (20 min) ────┼─► Run in PARALLEL
             │   ├─► Build (10 min) ───┤   Total: 20 min
             │   └─► Docs (10 min) ────┘
             │   ↓
             │   ✅ CI Pass → Can merge PR
             │
             ├─► Manual: Deploy to CAI (Workflow Dispatch)
             │   ↓
             │   Deploy Workflow (deploy-guardrails.yml) - MANUAL
             │   ├─► Setup Project (30 min)
             │   │   ↓ (outputs: project_id)
             │   ├─► Create Jobs (5 min)
             │   │   ↓ (sequential)
             │   ├─► Trigger Deployment (90 min)
             │   │   ↓ (sequential)
             │   └─► Verify Deployment (15 min)
             │   ↓
             │   ✅ Deployment Complete
             │
             └─► Release Published OR Manual Publish
                 ↓
                 Publish Workflow (publish.yml) - AUTO/MANUAL
                 ├─► Build Package (5 min)
                 ├─► Check Package (2 min)
                 └─► Publish to PyPI/Test PyPI (5 min)
                 ↓
                 ✅ Published to PyPI
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

## Workflow Trigger Reference

### CI Workflow (`ci.yml`)
| Trigger | Type | When | Action |
|---------|------|------|--------|
| push | Automatic | New code on main/develop | Run tests, lint, build |
| pull_request | Automatic | PR opened/updated to main/develop | Block merge if fail |
| No manual trigger | - | N/A | Always automatic |

**Code Location:**
```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

### Deploy Workflow (`deploy-guardrails.yml`)
| Trigger | Type | How | Parameters |
|---------|------|-----|------------|
| workflow_dispatch | Manual | GitHub UI or CLI | force_rebuild, enable_local_models |
| No automatic trigger | - | Must be manual | - |

**Manual Trigger via GitHub UI:**
1. Go to `Actions` tab
2. Select `Deploy NeMo Guardrails to CAI`
3. Click `Run workflow` button
4. Select options (optional)

**Manual Trigger via CLI:**
```bash
gh workflow run deploy-guardrails.yml \
  -f force_rebuild=false \
  -f enable_local_models=false
```

**Code Location:**
```yaml
on:
  workflow_dispatch:
    inputs:
      force_rebuild:
        description: 'Force rebuild'
        required: false
        default: false
        type: boolean
      enable_local_models:
        description: 'Enable local models'
        required: false
        default: false
        type: boolean
```

### Publish Workflow (`publish.yml`)
| Trigger | Type | When | Destination |
|---------|------|------|-------------|
| release published | Automatic | Create GitHub Release | PyPI (official) |
| workflow_dispatch | Manual | Manual trigger | Test PyPI |

**Automatic Trigger (Release):**
1. Create new Release on GitHub
2. Automatically publishes to PyPI
3. `if: github.event_name == 'release'`

**Manual Trigger (Test PyPI):**
1. GitHub UI → `Actions` → `Publish to PyPI`
2. Enter version number
3. Publishes to Test PyPI
4. `if: github.event_name == 'workflow_dispatch'`

**Code Location:**
```yaml
on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to publish'
        required: true
        type: string
```

## How Workflows Use Secrets

### Secret Storage
1. Repository Settings → `Secrets and variables` → `Actions`
2. Add each secret with name and value
3. Referenced in workflows as `${{ secrets.SECRET_NAME }}`

### CI Workflow
- **No secrets needed** (runs without authentication)

### Deploy Workflow
```yaml
env:
  CML_HOST: ${{ secrets.CML_HOST }}
  CML_API_KEY: ${{ secrets.CML_API_KEY }}
  GH_PAT: ${{ secrets.GH_PAT }}
```

### Publish Workflow
```yaml
env:
  TWINE_USERNAME: __token__
  TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}  # Automatic
  TWINE_PASSWORD: ${{ secrets.TEST_PYPI_API_TOKEN }}  # Manual
```

## How Workflows Access GitHub Context

### Available Context Variables
```yaml
github.repository      # "org/repo"
github.ref            # "refs/heads/main" or "refs/tags/v1.0.0"
github.ref_name       # "main" or "v1.0.0"
github.sha            # commit SHA
github.event_name     # "push", "pull_request", "release", "workflow_dispatch"
github.workflow       # workflow file name
github.event.inputs   # manual input parameters
```

### Example Usage in Workflows
```yaml
# Example 1: Use in log message
- run: echo "Deploying ${{ github.ref_name }} to CAI"

# Example 2: Conditional logic
- if: github.event_name == 'release'
  run: echo "This is a release"

# Example 3: Access manual inputs
- run: |
    python deploy.py \
      --force-rebuild=${{ github.event.inputs.force_rebuild }}
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Triggers Reference](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows)
- [GitHub CLI Manual](https://cli.github.com/manual)
- [CAI Integration Guide](../cai_integration/README.md)
- [Deployment Guide](../README.md#deploying-to-cloudera-ai-cml)

## Support

For issues with workflows:
- [GitHub Issues](https://github.com/cloudera/nemo-guardrails-cai/issues)
- Check workflow logs in Actions tab
- Review CAI project logs
