# NeMo Guardrails Deployment on CML

This directory contains scripts and configurations for deploying NeMo Guardrails on Cloudera Machine Learning (CML) using CAI infrastructure.

## Overview

The deployment system provides:

1. **Automated Project Creation** - Creates CML projects with git repository cloning
2. **Environment Setup** - Installs NeMo Guardrails and dependencies
3. **Application Deployment** - Deploys guardrails server as a CML Application
4. **Job Orchestration** - Manages job dependencies and sequencing

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           Deployment Pipeline                                │
└──┬───────────────┬──────────────────┬──────────────────────┘
   │               │                  │
   ▼               ▼                  ▼
┌─────────┐  ┌──────────┐  ┌──────────────────────┐
│ Setup   │  │ Create   │  │ Trigger              │
│ Project │─▶│ Jobs     │─▶│ Deployment           │
└─────────┘  └──────────┘  └──────────────────────┘
     │            │               │
     │            │               ▼
     │            │         ┌──────────┬──────────┬──────────┐
     │            │         │ Git Sync │  Setup   │ Launch   │
     │            └────────▶│ Job      │─▶Env Job │─▶Server  │
     │                      └──────────┘  └────────┘ └────────┘
     └────────────────────────────────────────────────┘
```

## Components

### 1. Project Setup (`setup_project.py`)

Creates or discovers CML project:
- Searches for existing project
- Creates new project with git repository
- Waits for git clone to complete
- Outputs project ID for subsequent steps

### 2. Job Management (`create_jobs.py`)

Creates CML jobs from configuration:
- Loads `jobs_config.yaml`
- Creates or updates job definitions
- Sets up job dependencies
- Outputs job IDs for execution

### 3. Job Execution (`trigger_jobs.py`)

Triggers jobs in sequence:
- Executes jobs in dependency order
- Monitors job completion with status updates
- Handles failures and errors
- Reports overall success/failure

### 4. Environment Setup (`setup_environment.py`)

Runs as a CML job to:
- Create Python virtual environment at `/home/cdsw/.venv`
- Install NeMo Guardrails and dependencies
- Verify installation

### 5. Guardrails Deployment (`launch_guardrails.py`)

Runs as a CML job to:
- Load deployment configuration
- Create CML Application for guardrails server
- Monitor startup
- Save connection info to `/home/cdsw/guardrails_info.json`

### 6. Job Configuration (`jobs_config.yaml`)

Defines the deployment job pipeline:
- **git_sync**: Clone/sync repository
- **setup_environment**: Install dependencies
- **launch_guardrails**: Deploy server application

## Setup Instructions

### Prerequisites

1. **CML Instance Access**
   - CML host URL
   - API key with project creation permissions

2. **GitHub Repository** (optional)
   - Repository with nemo-guardrails-cai code
   - GitHub token for private repos (if private)

3. **Guardrails Configuration**
   - NeMo Guardrails config directory (`config/`)
   - See [Configuration Guide](#configuration) below

### Deployment

#### Option 1: Automated Deployment

```bash
# Set environment variables
export CML_HOST="https://ml.example.cloudera.site"
export CML_API_KEY="your-api-key"
export GITHUB_REPOSITORY="owner/nemo-guardrails-cai"

# Run deployment
bash cai_integration/deploy.sh
```

#### Option 2: Step-by-Step Deployment

```bash
# Step 1: Setup project
python cai_integration/setup_project.py
PROJECT_ID=$(cat /tmp/project_id.txt)

# Step 2: Create jobs
python cai_integration/create_jobs.py --project-id $PROJECT_ID

# Step 3: Trigger deployment
python cai_integration/trigger_jobs.py \
  --project-id $PROJECT_ID \
  --jobs-config cai_integration/jobs_config.yaml
```

#### Option 3: Manual Deployment

```bash
# 1. Create project manually in CML UI
# 2. Clone repository
git clone https://github.com/owner/nemo-guardrails-cai.git
cd nemo-guardrails-cai

# 3. Run setup job
python cai_integration/setup_environment.py

# 4. Run deployment job
export CML_HOST="https://ml.example.cloudera.site"
export CML_API_KEY="your-api-key"
export CDSW_PROJECT_ID="your-project-id"
python cai_integration/launch_guardrails.py
```

## Configuration

### Guardrails Configuration

Create a `config/` directory with your guardrails configuration:

```
config/
├── config.yml          # Main configuration
├── prompts.yml         # Custom prompts (optional)
└── rails/
    ├── topical.co      # Topical rails
    ├── moderation.co   # Moderation rails
    └── facts.co        # Fact-checking rails (optional)
```

Example minimal `config/config.yml`:

```yaml
models:
  - type: main
    engine: openai
    model: gpt-3.5-turbo

rails:
  input:
    flows:
      - self check input
  output:
    flows:
      - self check output
```

### Deployment Configuration

Create `guardrails_config.yaml` in the project root:

```yaml
# Server configuration
server:
  cpu: 4
  memory: 16
  bypass_authentication: false
  # Port is automatically determined by CDSW_APP_PORT in CAI
  runtime_identifier: "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-pbj-jupyterlab-python3.11-standard:2025.09.1-b5"

# Guardrails configuration
guardrails:
  config_path: config
```

### Environment Variables

Required for deployment:

```bash
# CML Configuration
CML_HOST="https://ml.example.cloudera.site"
CML_API_KEY="your-api-key"

# Git Configuration (for new projects)
GITHUB_REPOSITORY="owner/repo"
GH_PAT="github-token"  # Optional for private repos

# LLM Configuration (runtime)
OPENAI_API_KEY="your-openai-key"  # Or other LLM provider key
```

## Monitoring & Troubleshooting

### View Application Status

```bash
# SSH into CML or check project files
cat /home/cdsw/guardrails_info.json
```

Example output:

```json
{
  "app_id": "abc-123",
  "app_name": "nemo-guardrails-server",
  "subdomain": "guardrails-xyz.ml.example.cloudera.site",
  "url": "https://guardrails-xyz.ml.example.cloudera.site",
  "status": "running"
}
```

### Test the Server

```bash
# Test health endpoint
curl https://guardrails-xyz.ml.example.cloudera.site/health

# Test chat completion
curl https://guardrails-xyz.ml.example.cloudera.site/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### View Logs

- **Project creation**: Check CML API responses in deployment logs
- **Git clone**: Check CML project status in UI
- **Job execution**: View in CML UI > Project > Jobs > Runs
- **Application**: View in CML UI > Project > Applications

### Common Issues

**Issue**: `nemoguardrails module not found`
- **Solution**: Check that setup_environment job completed successfully

**Issue**: `Config path not found`
- **Solution**: Ensure `config/` directory exists in repository root

**Issue**: `Application failed to start`
- **Solution**: Check application logs in CML UI for specific error

**Issue**: `OpenAI API key not set`
- **Solution**: Set `OPENAI_API_KEY` environment variable in application

## Advanced Usage

### Custom Guardrails

Add custom guardrails to `config/rails/`:

```colang
# config/rails/custom.co
define user ask about prices
  "How much does it cost"
  "What's the price"

define bot refuse pricing questions
  "I cannot provide pricing information. Please contact sales."

define flow
  user ask about prices
  bot refuse pricing questions
```

### Multiple Environments

Deploy to different environments:

```bash
# Development
export CML_HOST="https://ml-dev.example.cloudera.site"
python cai_integration/setup_project.py

# Production
export CML_HOST="https://ml-prod.example.cloudera.site"
python cai_integration/setup_project.py
```

### Custom Runtime

Specify a different Docker runtime in `guardrails_config.yaml`:

```yaml
server:
  runtime_identifier: "your-custom-runtime-identifier"
```

## Integration Examples

### Python Client

```python
from openai import OpenAI

# Connect to deployed guardrails
client = OpenAI(
    base_url="https://guardrails-xyz.ml.example.cloudera.site/v1",
    api_key="dummy"
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

### Curl

```bash
curl https://guardrails-xyz.ml.example.cloudera.site/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

## References

- [NeMo Guardrails Documentation](https://github.com/NVIDIA/NeMo-Guardrails)
- [Cloudera Machine Learning](https://docs.cloudera.com/machine-learning/)
- [CML REST API](https://docs.cloudera.com/machine-learning/cloud/api/topics/ml-api-v2.html)

## Support

For issues or questions:

1. Check the [main README](../README.md)
2. Review [examples](../examples/)
3. Open an [issue](https://github.com/cloudera/nemo-guardrails-cai/issues)

## License

See LICENSE file in repository root.
