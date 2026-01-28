# nemo-guardrails-cai

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![CI](https://github.com/cloudera/nemo-guardrails-cai/workflows/CI%20-%20Tests%20and%20Linting/badge.svg)](https://github.com/cloudera/nemo-guardrails-cai/actions)
[![Deploy to CAI](https://github.com/cloudera/nemo-guardrails-cai/workflows/Deploy%20NeMo%20Guardrails%20to%20CAI/badge.svg)](https://github.com/cloudera/nemo-guardrails-cai/actions)

**NVIDIA NeMo Guardrails deployment for Cloudera AI**

A production-ready Python package for deploying and managing NVIDIA NeMo Guardrails in Cloudera Machine Learning (CML) environments. Add programmable guardrails to your LLM applications with safety, security, and compliance controls.

## Features

- 🛡️ **Programmable Guardrails**: Add safety and compliance controls to LLM applications
- 🔌 **Easy Integration**: Simple Python API for deploying guardrails
- 🎯 **OpenAI-Compatible**: Works with any OpenAI-compatible LLM
- 🌐 **CAI-Based Deployment**: Deploy as CML Applications with automated setup
- ⚡ **Production-Ready**: Comprehensive logging, error handling, and monitoring
- 📝 **YAML Configuration**: Declarative guardrails configuration
- 🔧 **Flexible**: Support for multiple guardrail types (topical, factual, moderation)
- 🤖 **Local Model Support**: Host BERT/transformer models locally for fast, cost-effective checks

## What are NeMo Guardrails?

NVIDIA NeMo Guardrails is an open-source toolkit for adding programmable guardrails to LLM-based conversational systems. It provides:

- **Topical Rails**: Keep conversations on-topic
- **Fact-Checking**: Verify factual accuracy of responses
- **Moderation**: Filter inappropriate content
- **Dialog Management**: Control conversation flow
- **Custom Rails**: Build your own guardrails

## Installation

### Basic Installation

```bash
pip install nemo-guardrails-cai
```

### With CAI Support

```bash
pip install nemo-guardrails-cai[cai]
```

### With Local Model Support

For using locally hosted models (BERT, etc.) for guardrail checks:

```bash
pip install nemo-guardrails-cai[local-models]
```

This installs HuggingFace Transformers and PyTorch for running models like jailbreak detectors and toxicity classifiers.

### Development Installation

```bash
git clone https://github.com/cloudera/nemo-guardrails-cai.git
cd nemo-guardrails-cai
pip install -e ".[dev]"
```

## Quick Start

### Test Locally First (Recommended)

Before deploying, test the guardrails locally with default rails:

```bash
# 1. Install NeMo Guardrails
pip install nemoguardrails

# 2. Set your OpenAI API key
export OPENAI_API_KEY='your-key-here'

# 3. Start test server
python examples/local_test/test_server.py

# 4. In another terminal, run tests
python examples/local_test/test_client.py
```

See [Local Testing Guide](examples/local_test/README.md) for detailed instructions.

### Basic Usage

```python
from nemo_guardrails_cai import GuardrailsServer, GuardrailsConfig
from pathlib import Path

# Create configuration
config = GuardrailsConfig(
    config_path=Path("config"),  # Path to guardrails config directory
    llm_model="gpt-3.5-turbo",
    port=8080  # Default port for CAI (will be overridden by CDSW_APP_PORT in CAI)
)

# Create and start server
server = GuardrailsServer(config)
server.start()
```

### Using the Command Line

```bash
# Start server with default config (uses port 8080 by default)
nemo-guardrails-server --config-path config/

# Specify custom port
nemo-guardrails-server --config-path config/ --port 8080

# With custom configuration file
nemo-guardrails-server --config server_config.yaml
```

### Client Usage

Once the server is running, use it like any OpenAI-compatible API:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",  # Default port is 8080
    api_key="dummy"  # Not required for local deployment
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
```

## Deploying to Cloudera AI (CML)

> **Note:** This package is designed to run exclusively in Cloudera AI (CML) instances. The application automatically detects the CAI environment and uses the appropriate port configuration.

### Two Deployment Options

#### Option 1: Use as a Python Package
Install and use the package programmatically in your CAI projects:

```bash
pip install nemo-guardrails-cai
```

See the "Quick Start" section above for usage examples.

#### Option 2: Run as a CAI Application (Recommended)

Deploy as a standalone web service in CAI. This is the primary deployment method.

**Prerequisites:**
1. **CML Instance Access**
   - CML host URL
   - API key with project creation permissions
2. **Guardrails Configuration**
   - Prepared `config/` directory with your guardrails rules

**Quick Deployment:**

```bash
# In your CAI workspace
cd /home/cdsw

# Clone or upload your project
git clone <your-repo-url>
cd nemo-guardrails-cai

# Ensure config directory exists
ls config/  # Should contain your guardrails configuration

# Run directly as CAI Application
python app.py
```

The application will:
- Automatically detect `CDSW_APP_PORT` (set by CAI)
- Use port 8080 as default fallback
- Start the guardrails server on `0.0.0.0`
- Expose OpenAI-compatible API endpoints

**Automated Deployment via CML API:**

```bash
# Set environment variables
export CML_HOST="https://ml.example.cloudera.site"
export CML_API_KEY="your-api-key"
export GITHUB_REPOSITORY="owner/nemo-guardrails-cai"

# Step 1: Setup project
python cai_integration/setup_project.py
PROJECT_ID=$(cat /tmp/project_id.txt)

# Step 2: Create jobs
python cai_integration/create_jobs.py --project-id $PROJECT_ID

# Step 3: Trigger deployment
python cai_integration/trigger_jobs.py --project-id $PROJECT_ID
```

The deployment will:
1. Create a CML project and sync from git
2. Setup Python environment with NeMo Guardrails
3. Deploy guardrails server as a CML Application
4. Save connection info to `/home/cdsw/guardrails_info.json`

See [CAI Integration Guide](cai_integration/README.md) for detailed instructions.

## Local Model Hosting

You can host classification models (e.g., BERT) locally in CAI for fast, cost-effective guardrail checks:

```yaml
# server_config.yaml
local_models:
  jailbreak_detector:
    type: huggingface
    model_name: "protectai/deberta-v3-base-prompt-injection-v2"
    device: cpu  # or 'cuda' for GPU
    threshold: 0.7

  toxicity_detector:
    type: huggingface
    model_name: "unitary/toxic-bert"
    device: cpu
    threshold: 0.5
```

Use in guardrails flows:

```colang
define flow
  user ...
  $is_jailbreak = execute check_jailbreak_local

  if $is_jailbreak
    bot refuse to respond
    stop
```

**Benefits:**
- ⚡ **Fast**: 20-100ms latency vs. seconds for LLM calls
- 💰 **Cost-effective**: No API costs for checks
- 🔒 **Private**: Data stays in your CAI environment
- 🎯 **Specialized**: Use fine-tuned models for specific checks

See [Local Models Guide](docs/LOCAL_MODELS.md) for detailed setup instructions.

## Configuration

### Guardrails Configuration

Create a `config/` directory with your guardrails configuration:

```
config/
├── config.yml          # Main configuration
├── prompts.yml         # Custom prompts
└── rails/
    ├── topical.co      # Topical rails
    ├── moderation.co   # Moderation rails
    └── facts.co        # Fact-checking rails
```

Example `config.yml`:

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
      - self check facts
```

### Server Configuration

Create a `server_config.yaml`:

```yaml
# Path to guardrails configuration directory
config_path: config

# Server settings
server:
  host: 0.0.0.0
  port: 8080  # Default port for CAI (overridden by CDSW_APP_PORT in CAI)
  streaming: true
  log_level: INFO

# LLM configuration
llm:
  provider: openai
  model: gpt-3.5-turbo
  api_key: ${OPENAI_API_KEY}
  api_base: https://api.openai.com/v1
```

### CML Deployment Configuration

Create a `guardrails_config.yaml` for CML deployment:

```yaml
# Server configuration
server:
  cpu: 4
  memory: 16
  bypass_authentication: false
  # Port is automatically determined by CDSW_APP_PORT in CAI

# Guardrails configuration
guardrails:
  config_path: config
```

## Examples

### Example 1: Basic Topical Rails

```python
# In config/rails/topical.co
define user ask about weather
  "What's the weather"
  "Is it sunny"

define bot refuse to answer
  "I can only help with programming questions."

define flow
  user ask about weather
  bot refuse to answer
```

### Example 2: Fact-Checking

```python
# In config/rails/facts.co
define flow
  user ...
  $answer = bot respond
  $is_accurate = execute fact_check(answer=$answer)

  if not $is_accurate
    bot inform answer might be incorrect
  else
    bot $answer
```

### Example 3: Content Moderation

```python
# In config/rails/moderation.co
define bot inform cannot respond
  "I cannot respond to that type of request."

define flow
  user ...
  $is_appropriate = execute check_jailbreak

  if not $is_appropriate
    bot inform cannot respond
    stop
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│          nemo_guardrails_cai                    │
│         (Python Package)                        │
└────────────┬────────────────────────────────────┘
             │
             ├─► GuardrailsServer
             │   • FastAPI server wrapper
             │   • Configuration management
             │   • Health monitoring
             │
             └─► GuardrailsConfig
                 • YAML configuration
                 • Environment variables
                 • Validation

┌─────────────────────────────────────────────────┐
│          cai_integration                        │
│         (CML Deployment)                        │
└────────────┬────────────────────────────────────┘
             │
             ├─► setup_project.py     # Project setup
             ├─► create_jobs.py       # Job creation
             ├─► trigger_jobs.py      # Job execution
             └─► launch_guardrails.py # Application deployment
```

## Use Cases

### 1. Customer Support Chatbots

Keep conversations on-topic and filter inappropriate content:

```yaml
rails:
  - topical: customer_support
  - moderation: sensitive_content
  - factual: product_information
```

### 2. Internal Knowledge Assistants

Ensure responses are factually accurate and within scope:

```yaml
rails:
  - topical: company_policies
  - factual: knowledge_base_verification
  - security: data_protection
```

### 3. Educational Tutors

Maintain educational focus and age-appropriate content:

```yaml
rails:
  - topical: educational_content
  - moderation: age_appropriate
  - pedagogical: learning_objectives
```

## Requirements

- Python 3.9+
- NeMo Guardrails >= 0.9.0
- FastAPI >= 0.109.0
- For CAI deployment: CML instance with API access

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Resources

- **[NeMo Guardrails Documentation](https://github.com/NVIDIA/NeMo-Guardrails)**
- **[CML Documentation](https://docs.cloudera.com/machine-learning/)**
- **[CAI Integration Guide](cai_integration/README.md)** - Automated deployment
- **[Local Models Guide](docs/LOCAL_MODELS.md)** - Host models locally in CAI
- **[Examples Directory](examples/)** - Working examples and configurations

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/cloudera/nemo-guardrails-cai/issues)
- 💬 [Discussions](https://github.com/cloudera/nemo-guardrails-cai/discussions)

## Acknowledgments

- **NVIDIA** - For the excellent NeMo Guardrails toolkit
- **Cloudera** - For supporting open-source ML infrastructure
- **FastAPI Team** - For the high-performance web framework

---

**Made with ❤️ for the Cloudera AI community**
