# GitHub Actions Workflow Summary

## Quick Overview

The project has **3 main workflows** organized by purpose:

### 1. **CI Workflow** - Quality Assurance
- **File:** `.github/workflows/ci.yml`
- **Trigger:** Automatic (push/PR to main/develop)
- **Jobs:** Lint, Test, Build, Docs (run in parallel)
- **Duration:** ~20 minutes
- **Purpose:** Catch bugs and quality issues before merge

### 2. **Deploy Workflow** - CAI Deployment
- **File:** `.github/workflows/deploy-guardrails.yml`
- **Trigger:** Manual (GitHub UI or CLI)
- **Jobs:** Setup → Create → Trigger → Verify (sequential)
- **Duration:** ~140 minutes
- **Purpose:** Deploy guardrails to Cloudera AI platform

### 3. **Publish Workflow** - PyPI Publishing
- **File:** `.github/workflows/publish.yml`
- **Trigger:** Automatic (release) or Manual (workflow dispatch)
- **Jobs:** Build → Check → Publish (single job)
- **Duration:** ~15 minutes
- **Purpose:** Publish package to Python Package Index

---

## How Each Workflow Is Triggered

### Trigger Type: AUTOMATIC

**CI Workflow:**
```
Developer Action          GitHub Event              Workflow Result
┌──────────────────────────────────────────────────────────────┐
│ 1. git push origin main                                      │
│    ↓                                                          │
│    GitHub detects: "push to main"                            │
│    ↓                                                          │
│    ci.yml trigger matches: on.push.branches=[main, develop] │
│    ↓                                                          │
│    ✅ Automatically starts CI jobs (lint, test, build)       │
│                                                              │
│ 2. Create Pull Request to main                              │
│    ↓                                                          │
│    GitHub detects: "pull_request to main"                   │
│    ↓                                                          │
│    ci.yml trigger matches: on.pull_request.branches=[main]  │
│    ↓                                                          │
│    ✅ Automatically starts CI jobs                           │
└──────────────────────────────────────────────────────────────┘
```

**Publish Workflow (Release):**
```
Developer Action          GitHub Event              Workflow Result
┌──────────────────────────────────────────────────────────────┐
│ 1. Create GitHub Release (UI or CLI)                         │
│    ↓                                                          │
│    GitHub detects: "release published"                      │
│    ↓                                                          │
│    publish.yml trigger matches: on.release.types=[published]│
│    ↓                                                          │
│    ✅ Automatically publishes to PyPI                        │
└──────────────────────────────────────────────────────────────┘
```

### Trigger Type: MANUAL

**Deploy Workflow:**
```
Developer Action                GitHub Action              Workflow Result
┌────────────────────────────────────────────────────────────────────┐
│ 1. GitHub UI (Browser)                                             │
│    → Go to: Actions tab                                            │
│    → Select: "Deploy NeMo Guardrails to CAI"                       │
│    → Click: "Run workflow" button                                  │
│    → Optional: Set force_rebuild, enable_local_models              │
│    → Click: "Run workflow"                                         │
│    ↓                                                               │
│    ✅ deploy-guardrails.yml starts with manual parameters          │
│                                                                    │
│ 2. GitHub CLI                                                      │
│    $ gh workflow run deploy-guardrails.yml \                       │
│        -f force_rebuild=false \                                    │
│        -f enable_local_models=false                                │
│    ↓                                                               │
│    ✅ deploy-guardrails.yml starts with provided parameters        │
└────────────────────────────────────────────────────────────────────┘
```

**Publish Workflow (Manual):**
```
Developer Action                GitHub Action              Workflow Result
┌────────────────────────────────────────────────────────────────────┐
│ 1. GitHub UI (Browser)                                             │
│    → Go to: Actions tab                                            │
│    → Select: "Publish to PyPI"                                     │
│    → Click: "Run workflow" button                                  │
│    → Input: version = "0.1.0-beta" (or any version)                │
│    → Click: "Run workflow"                                         │
│    ↓                                                               │
│    ✅ publish.yml starts in manual mode                            │
│       (publishes to Test PyPI, not official PyPI)                  │
│                                                                    │
│ 2. GitHub CLI                                                      │
│    $ gh workflow run publish.yml -f version=0.1.0                  │
│    ↓                                                               │
│    ✅ publish.yml starts in manual mode                            │
└────────────────────────────────────────────────────────────────────┘
```

---

## Job Execution Patterns

### Pattern 1: PARALLEL Jobs (CI Workflow)
```
Trigger: push to main
    ↓
┌─────────────────────────────────┐
│ Start all jobs at once:         │
│                                 │
│  Job: lint       (10 min) ────┐ │
│  Job: test       (20 min) ────┼─► Run simultaneously
│  Job: build      (10 min) ────┤ │  Total: 20 min
│  Job: docs       (10 min) ────┘ │
└─────────────────────────────────┘
    ↓
Wait for slowest (test: 20 min)
    ↓
Result: All pass or any fail
```

### Pattern 2: SEQUENTIAL Jobs (Deploy Workflow)
```
Trigger: Manual workflow dispatch
    ↓
Job 1: setup-project (30 min)
  └─► output: project_id
    ↓
Job 2: create-jobs (5 min)
  └─► needs: setup-project
      uses: project_id from Job 1
    ↓
Job 3: trigger-deployment (90 min)
  └─► needs: setup-project, create-jobs
      uses: project_id from Job 1
    ↓
Job 4: verify-deployment (15 min)
  └─► needs: trigger-deployment
      if: trigger-deployment succeeded
    ↓
Result: Total ~140 minutes
```

### Pattern 3: CONDITIONAL Publishing (Publish Workflow)
```
Workflow starts
    ↓
Build package
    ↓
Check package
    ↓
Branch 1: If github.event_name == 'release'
  └─► Publish to PyPI (official)

Branch 2: If github.event_name == 'workflow_dispatch'
  └─► Publish to Test PyPI (testing)
    ↓
Result: Published to appropriate destination
```

---

## How Data Flows Between Jobs

### Output from One Job to Another

```yaml
# Job 1: setup-project
jobs:
  setup-project:
    runs-on: ubuntu-latest
    outputs:
      project_id: ${{ steps.setup.outputs.project_id }}
    steps:
      - id: setup
        run: |
          PROJECT_ID=$(cat /tmp/project_id.txt)
          echo "project_id=$PROJECT_ID" >> $GITHUB_OUTPUT

# Job 2: create-jobs (depends on setup-project)
  create-jobs:
    needs: setup-project  # ← Declares dependency
    steps:
      - run: |
          # Access output from previous job
          python create_jobs.py --project-id ${{ needs.setup-project.outputs.project_id }}
```

**Output Flow:**
```
Job 1 runs
  ↓
Set output: project_id=12345
  ↓
Job 2 starts (after Job 1 complete)
  ↓
Access: ${{ needs.setup-project.outputs.project_id }}
  ↓
Use value: project_id=12345
```

---

## Environment & Secrets

### Where Secrets Come From
```
Repository Settings
    ↓
Secrets and variables
    ↓
Actions → New repository secret
    ↓
Add: CML_HOST, CML_API_KEY, PYPI_API_TOKEN, etc.
    ↓
Workflows reference as: ${{ secrets.SECRET_NAME }}
```

### Example Secret Usage
```yaml
env:
  CML_HOST: ${{ secrets.CML_HOST }}        # Hidden from logs
  CML_API_KEY: ${{ secrets.CML_API_KEY }}  # Hidden from logs

steps:
  - run: python deploy.py  # Uses env vars, values not visible
    # Logs show: python deploy.py
    # Actual command: python deploy.py (with real values)
```

---

## Quick Reference: How to Trigger Each Workflow

### Trigger CI (Automatic)
```bash
# Just push code!
git add .
git commit -m "my changes"
git push origin main

# CI automatically runs
# View in: GitHub UI → Actions tab
```

### Trigger Deploy (Manual)
```bash
# Option 1: GitHub UI
GitHub → Actions → "Deploy NeMo Guardrails to CAI" → Run workflow

# Option 2: CLI
gh workflow run deploy-guardrails.yml

# View progress in: GitHub UI → Actions tab
```

### Trigger Publish (Auto + Manual)
```bash
# Automatic: Create Release
# GitHub UI → Code → Releases → Create new release → Publish

# Manual: Test PyPI
# GitHub UI → Actions → "Publish to PyPI" → Run workflow
# Input version: 0.1.0-beta
# Publishes to Test PyPI

# View in: GitHub UI → Actions tab or PyPI website
```

---

## Common Scenarios

### Scenario 1: Daily Development
```
1. Developer makes changes
   ↓
2. git push to develop branch
   ↓
3. GitHub detects push → ci.yml auto-runs
   ↓
4. Tests/lint/build run in parallel (20 min)
   ↓
5. Results: ✅ Pass or ❌ Fail shown in commit status
```

### Scenario 2: Deploying to CAI
```
1. All tests pass in main branch
   ↓
2. Developer clicks: Actions → Deploy → Run workflow
   ↓
3. Parameters: force_rebuild=false, enable_local_models=true
   ↓
4. deploy-guardrails.yml runs sequentially (140 min)
   ↓
5. Result: Guardrails running on CAI
```

### Scenario 3: Publishing Release
```
1. All tests pass, code ready
   ↓
2. Update version in pyproject.toml
   ↓
3. Create GitHub Release (GitHub UI)
   ↓
4. GitHub detects release → publish.yml auto-runs
   ↓
5. Result: Package published to PyPI automatically
```

---

## Updated Documentation

The `.github/README.md` file has been updated with:
- ✅ Detailed workflow organization
- ✅ How each workflow is triggered
- ✅ Job execution patterns (parallel vs sequential)
- ✅ Data flow between jobs
- ✅ How secrets and environment variables work
- ✅ Complete reference tables
- ✅ Quick reference guides
- ✅ Common scenarios and examples
