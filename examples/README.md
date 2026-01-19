# NeMo Guardrails CAI - Examples

This directory contains working examples for different use cases.

## Directory Structure

```
examples/
├── README.md                                    # This file
├── basic_usage.py                               # Simple Python usage
├── client_usage.py                              # Client examples
│
├── config/                                      # Basic configuration
│   ├── config.yml                               # Main config (uses built-in rails)
│   └── rails/
│       ├── topical.co                           # Custom topical rails
│       └── moderation.co                        # Custom moderation rails
│
├── config_with_local_models/                    # With local models
│   ├── config.yml                               # Config using local model checks
│   └── rails/
│       └── local_model_checks.co                # Flows using local models
│
├── server_config.yaml                           # Server config (basic)
├── server_config_with_local_models.yaml         # Server config (with local models)
└── guardrails_config.yaml                       # CML deployment config
```

## Examples Overview

### 1. Basic Configuration (config/)

**What it demonstrates:**
- Using built-in NeMo Guardrails features
- Mix of built-in rails (`self check input`) and custom rails
- Standard LLM-based checks

**Key files:**
- [config/config.yml](config/config.yml) - References built-in `self check input/output`
- [config/rails/topical.co](config/rails/topical.co) - Custom topical constraints
- [config/rails/moderation.co](config/rails/moderation.co) - Custom moderation flows

**Use this when:**
- You want standard NeMo Guardrails functionality
- You're okay with LLM-based checks (slower but comprehensive)
- You don't need specialized models

### 2. Configuration with Local Models (config_with_local_models/)

**What it demonstrates:**
- Hosting BERT models locally for fast checks
- Custom actions using local models
- Hybrid approach (built-in + local models)

**Key files:**
- [config_with_local_models/config.yml](config_with_local_models/config.yml) - Config using local model flows
- [config_with_local_models/rails/local_model_checks.co](config_with_local_models/rails/local_model_checks.co) - Flows using `check_jailbreak_local`
- [server_config_with_local_models.yaml](server_config_with_local_models.yaml) - Full server config with model definitions

**Use this when:**
- You need fast checks (20-100ms vs seconds)
- You want to reduce API costs
- You have specific models for jailbreak/toxicity detection
- Running in CAI with sufficient resources

### 3. Python Usage Examples

**[basic_usage.py](basic_usage.py)**
- How to create a GuardrailsServer programmatically
- Configuration in Python code
- Testing the server

**[client_usage.py](client_usage.py)**
- Using OpenAI client to interact with guardrails
- Making requests to the server
- Handling responses

## Quick Start

### Running Basic Example

```bash
# Start server with basic config
cd examples
nemo-guardrails-server --config server_config.yaml

# Or run directly
python -m nemo_guardrails_cai.server --config-path config/
```

### Running with Local Models

```bash
# Install dependencies first
pip install nemo-guardrails-cai[local-models]

# Start server with local models
cd examples
nemo-guardrails-server --config server_config_with_local_models.yaml
```

The server will:
1. Load local models (jailbreak detector, toxicity detector)
2. Initialize NeMo Guardrails with your config
3. Start on port 8080 (or CDSW_APP_PORT in CAI)

### Testing the Server

```bash
# In another terminal
python client_usage.py
```

Or use curl:

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

## Understanding Rails Location

### Built-in Rails (from NeMo Guardrails)

These are **already defined** in the NeMo Guardrails library:

```yaml
# In your config.yml - these just reference built-in flows
rails:
  input:
    flows:
      - self check input      # Built-in flow (in NeMo library)
  output:
    flows:
      - self check output     # Built-in flow (in NeMo library)
      - self check facts      # Built-in flow (in NeMo library)
```

You **don't need** to create `.co` files for these - they're in the NeMo package.

### Your Custom Rails

These are **defined by you** in `config/rails/*.co`:

```yaml
# In your config.yml
rails:
  input:
    flows:
      - check jailbreak with local model  # Your custom flow
      - check toxic content               # Your custom flow
```

```colang
# In config/rails/custom_checks.co
define flow check jailbreak with local model
  user ...
  $is_jailbreak = execute check_jailbreak_local

  if $is_jailbreak
    bot refuse to respond
    stop
```

See [RAILS_STRUCTURE.md](../docs/RAILS_STRUCTURE.md) for more details.

## Configuration Comparison

### Basic Config (LLM-based)

```yaml
# config/config.yml
rails:
  input:
    flows:
      - self check input          # Uses LLM (~1-3 seconds)
      - check jailbreak           # Uses LLM (~1-3 seconds)
```

**Pros:**
- ✅ No additional models to host
- ✅ Comprehensive checking
- ✅ Easy to configure

**Cons:**
- ❌ Slower (seconds per check)
- ❌ API costs
- ❌ Requires internet/LLM access

### With Local Models

```yaml
# config_with_local_models/config.yml
rails:
  input:
    flows:
      - check jailbreak with local model  # Uses BERT (~50ms)
      - check toxicity with local model   # Uses BERT (~50ms)
```

```yaml
# server_config_with_local_models.yaml
local_models:
  jailbreak_detector:
    type: huggingface
    model_name: "protectai/deberta-v3-base-prompt-injection-v2"
```

**Pros:**
- ✅ Very fast (20-100ms)
- ✅ No API costs
- ✅ Works offline
- ✅ Data stays local

**Cons:**
- ❌ Need to host models
- ❌ Requires CPU/GPU resources
- ❌ More setup complexity

## Model Requirements

### Basic Config
- **Memory:** ~500MB
- **CPU:** 2+ cores recommended
- **Dependencies:** Just NeMo Guardrails

### With Local Models
- **Memory:** 2-4GB (depends on models)
- **CPU:** 4+ cores recommended (or GPU)
- **Dependencies:** transformers, torch
- **Disk:** ~1GB per model

## CAI Deployment

### Basic Deployment

```yaml
# guardrails_config.yaml
server:
  cpu: 2
  memory: 4  # GB
```

### With Local Models

```yaml
# guardrails_config.yaml
server:
  cpu: 4
  memory: 8  # GB (need more for models)
```

For GPU acceleration in CAI:
```yaml
server:
  cpu: 4
  memory: 16
  gpu: 1  # If available in your CML instance
```

## Choosing the Right Example

| Use Case | Example to Use |
|----------|----------------|
| Getting started | `config/` (basic) |
| Production with LLM checks | `config/` (basic) |
| Fast, cost-effective checks | `config_with_local_models/` |
| Custom models | `config_with_local_models/` (modify) |
| Offline deployment | `config_with_local_models/` |
| Low latency required | `config_with_local_models/` |

## Troubleshooting

### "Model not found in registry"

You're trying to use local models but haven't configured them:

**Solution:** Use `server_config_with_local_models.yaml` which includes model definitions.

### "Built-in rail not working"

Built-in rails like `self check input` require LLM access:

**Solution:** Ensure OPENAI_API_KEY is set or configure your LLM endpoint.

### "Out of memory"

Local models are consuming too much RAM:

**Solution:**
1. Use smaller models (e.g., distilbert)
2. Increase CAI workspace memory
3. Use CPU instead of trying to load all models

## Next Steps

- [Local Models Guide](../docs/LOCAL_MODELS.md) - Deep dive into local models
- [Rails Structure](../docs/RAILS_STRUCTURE.md) - Understanding rails organization
- [CAI Integration](../cai_integration/README.md) - Automated deployment

## Support

For questions or issues:
- [GitHub Issues](https://github.com/cloudera/nemo-guardrails-cai/issues)
- [Documentation](../docs/)
