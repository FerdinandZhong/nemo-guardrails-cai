# Getting Started with NeMo Guardrails CAI

This guide will walk you through testing NeMo Guardrails locally and deploying to CAI.

## Overview

```
1. Test Locally (5 minutes)
   ↓
2. Understand Configuration (10 minutes)
   ↓
3. Deploy to CAI (30 minutes)
   ↓
4. Add Local Models (optional, 15 minutes)
```

## Step 1: Test Locally (5 minutes)

Test the guardrails on your local machine first.

### Prerequisites

- Python 3.9+
- OpenAI API key

### Quick Test

```bash
# 1. Install NeMo Guardrails
pip install nemoguardrails

# 2. Set OpenAI API key
export OPENAI_API_KEY='sk-...'

# 3. Start server
python examples/local_test/test_server.py
```

In another terminal:

```bash
# 4. Run tests
python examples/local_test/test_client.py
```

You should see:

```
🧪 Testing NeMo Guardrails with Default Rails
======================================================================

Test 1/6: Normal Query ✅ PASS
Test 2/6: Jailbreak Attempt #1 ✅ PASS (blocked)
Test 3/6: Jailbreak Attempt #2 ✅ PASS (blocked)
...

📊 Test Summary
Tests Passed: 6/6
🎉 All tests passed!
```

**What just happened?**

The default rails (`self check input` and `self check output`) used OpenAI to:
1. Check user input for jailbreaks → Blocked malicious attempts
2. Check LLM output for safety → Ensured safe responses
3. Allow legitimate queries → Normal operation

See [Local Testing Guide](examples/local_test/README.md) for details.

## Step 2: Understand Configuration (10 minutes)

### Default Rails (What You Just Tested)

**Minimal config** - uses built-in NeMo rails:

```yaml
# examples/local_test/config.yml
models:
  - type: main
    engine: openai
    model: gpt-3.5-turbo

rails:
  input:
    flows:
      - self check input   # Built-in: checks jailbreaks
  output:
    flows:
      - self check output  # Built-in: checks safety
```

**Pros:**
- ✅ Easy to set up
- ✅ Comprehensive checks
- ✅ No custom code needed

**Cons:**
- ❌ Slow (2-3 seconds per request)
- ❌ Costs money (3 LLM calls per request)

### With Local Models (Faster & Free)

**Enhanced config** - uses local BERT models:

```yaml
# examples/server_config_with_local_models.yaml
models:
  - type: main
    engine: openai
    model: gpt-3.5-turbo

# Local models for fast checks
local_models:
  jailbreak_detector:
    type: huggingface
    model_name: "protectai/deberta-v3-base-prompt-injection-v2"
    device: cpu
    threshold: 0.7

rails:
  input:
    flows:
      - check jailbreak with local model  # Fast (50ms)
      - self check input                   # Backup (2s)
```

**Pros:**
- ✅ Very fast (50ms for local check)
- ✅ Free (no API costs for checks)
- ✅ Private (data stays local)

**Cons:**
- ❌ Requires more setup
- ❌ Needs model installation

See [Local Models Guide](docs/LOCAL_MODELS.md) for setup.

### Custom Rails (Advanced)

Create your own checks:

```colang
# config/rails/custom.co
define bot refuse inappropriate
  "I cannot help with that request."

define flow check custom rule
  user ...
  $meets_criteria = execute my_custom_check

  if not $meets_criteria
    bot refuse inappropriate
    stop
```

See [Rails Structure Guide](docs/RAILS_STRUCTURE.md) for details.

## Step 3: Deploy to CAI (30 minutes)

Deploy to Cloudera AI for production use.

### Prerequisites

1. **CAI Access**
   - CML instance URL
   - API key with project permissions

2. **GitHub Setup**
   - Fork this repository (or use your own)
   - GitHub Personal Access Token

### Option A: Manual Deployment

```bash
# 1. Set environment variables
export CML_HOST="https://ml.example.cloudera.site"
export CML_API_KEY="your-api-key"
export GITHUB_REPOSITORY="your-org/nemo-guardrails-cai"

# 2. Setup project
python cai_integration/setup_project.py
PROJECT_ID=$(cat /tmp/project_id.txt)

# 3. Create jobs
python cai_integration/create_jobs.py --project-id $PROJECT_ID

# 4. Trigger deployment
python cai_integration/trigger_jobs.py --project-id $PROJECT_ID
```

### Option B: GitHub Actions (Recommended)

1. **Configure Secrets** in GitHub repo settings:
   ```
   CML_HOST = https://ml.example.cloudera.site
   CML_API_KEY = your-api-key
   GH_PAT = your-github-token
   ```

2. **Run Workflow**:
   - Go to Actions tab
   - Select "Deploy NeMo Guardrails to CAI"
   - Click "Run workflow"

3. **Monitor Progress**:
   - Watch workflow logs
   - Check CAI project for status

4. **Get Endpoint**:
   - Check `guardrails_info.json` in CAI project
   - Use the URL provided

See [CAI Integration Guide](cai_integration/README.md) for details.

### Deployment Architecture

```
GitHub Repository
    ↓
CAI Project Created
    ↓
Jobs Run Sequentially:
  1. git_sync       → Clone repo
  2. setup_env      → Install dependencies
  3. launch_server  → Start guardrails
    ↓
Application Running
  - OpenAI-compatible API
  - Port: CDSW_APP_PORT (auto-detected)
  - Health check: /health
```

### Verify Deployment

```bash
# Get connection info
cat /home/cdsw/guardrails_info.json

# Test endpoint
curl https://YOUR-APP-URL/health
```

## Step 4: Add Local Models (Optional, 15 minutes)

Speed up checks with local BERT models.

### Install Dependencies

In CAI workspace:

```bash
pip install nemo-guardrails-cai[local-models]
```

### Update Configuration

```yaml
# server_config.yaml
local_models:
  jailbreak_detector:
    type: huggingface
    model_name: "protectai/deberta-v3-base-prompt-injection-v2"
    device: cpu
    auto_load: true
```

### Use in Rails

```colang
# config/rails/checks.co
define flow
  user ...
  $is_jailbreak = execute check_jailbreak_local

  if $is_jailbreak
    bot refuse to respond
    stop
```

### Performance Comparison

| Approach | Latency | Cost |
|----------|---------|------|
| LLM-based (default) | 2-3s | $0.003/req |
| Local models | 50ms | $0 |
| Hybrid (recommended) | 150ms | $0.0003/req |

See [Model Comparison](docs/MODEL_COMPARISON.md) for details.

## Common Use Cases

### 1. Customer Support Chatbot

**Requirements:**
- Block jailbreaks
- Keep on-topic
- Fast responses

**Configuration:**
```yaml
local_models:
  jailbreak_detector: {...}

rails:
  input:
    flows:
      - check jailbreak with local model
      - check if on topic
```

**Result:** 50ms checks, 90% cost savings

### 2. Internal Knowledge Bot

**Requirements:**
- Fact-checking
- Data privacy
- Offline capable

**Configuration:**
```yaml
local_models:
  jailbreak_detector: {...}
  fact_checker: {...}

rails:
  input:
    flows:
      - check jailbreak with local model
  output:
    flows:
      - check facts with local model
```

**Result:** All processing stays in CAI, no external API calls

### 3. Development/Testing

**Requirements:**
- Quick iteration
- Low cost
- Easy debugging

**Configuration:**
```yaml
# Use defaults, no local models needed
rails:
  input:
    flows:
      - self check input
```

**Result:** Simple setup, comprehensive checks

## Troubleshooting

### Local Testing Issues

**Problem:** Server won't start

```bash
# Check if NeMo Guardrails is installed
pip install nemoguardrails

# Check if API key is set
echo $OPENAI_API_KEY
```

**Problem:** Tests fail

- Check internet connection
- Verify OpenAI API key is valid
- Check API quota/billing

### CAI Deployment Issues

**Problem:** Project creation fails

```bash
# Verify credentials
python -c "
from caikit import CMLClient
client = CMLClient(host='$CML_HOST', api_key='$CML_API_KEY')
print('✅ Connected')
"
```

**Problem:** Jobs timeout

- Increase timeout in `jobs_config.yaml`
- Check CAI workspace resources
- View job logs in CAI UI

### Local Models Issues

**Problem:** Out of memory

- Use smaller models (distilbert)
- Reduce batch_size to 1
- Switch to CPU mode
- Increase CAI memory allocation

## Next Steps

### Learn More

- [Local Models Guide](docs/LOCAL_MODELS.md) - Deep dive into local models
- [Rails Implementation](docs/RAILS_IMPLEMENTATION.md) - How rails work
- [Model Comparison](docs/MODEL_COMPARISON.md) - Choose the right approach

### Examples

- [Basic Config](examples/config/) - Default rails
- [With Local Models](examples/config_with_local_models/) - Fast checks
- [Local Testing](examples/local_test/) - Test before deploying

### Development

- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [GitHub Workflows](.github/README.md) - Automation

## Quick Reference

### Commands Cheat Sheet

```bash
# Local testing
python examples/local_test/test_server.py
python examples/local_test/test_client.py

# CAI deployment
python cai_integration/setup_project.py
python cai_integration/create_jobs.py --project-id <id>
python cai_integration/trigger_jobs.py --project-id <id>

# GitHub Actions
gh workflow run deploy-guardrails.yml

# Check status
curl http://localhost:8080/health           # Local
curl https://your-app-url/health            # CAI
```

### Configuration Templates

**Minimal (LLM-based):**
```yaml
models:
  - type: main
    engine: openai
    model: gpt-3.5-turbo

rails:
  input:
    flows:
      - self check input
```

**Optimal (Hybrid):**
```yaml
models:
  - type: main
    engine: openai
    model: gpt-3.5-turbo

local_models:
  jailbreak_detector:
    type: huggingface
    model_name: "protectai/deberta-v3-base-prompt-injection-v2"

rails:
  input:
    flows:
      - check jailbreak with local model
      - self check input  # Backup
```

## Support

- **Issues**: [GitHub Issues](https://github.com/cloudera/nemo-guardrails-cai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/cloudera/nemo-guardrails-cai/discussions)
- **Documentation**: [docs/](docs/)

## Summary

**You've learned:**
1. ✅ How to test locally with default rails
2. ✅ Configuration options (LLM vs. local models)
3. ✅ How to deploy to CAI
4. ✅ When to use local models
5. ✅ Common use cases and troubleshooting

**Recommended path:**
1. Start with local testing (default rails)
2. Deploy to CAI with default config
3. Add local models for performance
4. Fine-tune for your use case

Happy guardrailing! 🛡️
