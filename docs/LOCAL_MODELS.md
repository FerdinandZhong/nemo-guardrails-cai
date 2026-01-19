# Local Model Hosting for NeMo Guardrails in CAI

This guide explains how to use locally hosted models (e.g., BERT-based classifiers) for guardrail checks in Cloudera AI (CAI).

## Overview

Instead of relying solely on LLM-based checks, you can host specialized classification models locally in CAI for specific guardrail tasks:

- **Jailbreak Detection**: Detect prompt injection and jailbreak attempts
- **Toxicity Detection**: Filter toxic and offensive content
- **Custom Classifications**: Use fine-tuned models for domain-specific checks

## Benefits

✅ **Lower Latency**: Local models respond faster than API calls
✅ **Cost Effective**: No API costs for guardrail checks
✅ **Privacy**: Data stays within your CAI environment
✅ **Customizable**: Use your own fine-tuned models
✅ **Offline Capable**: Works without external dependencies

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                NeMo Guardrails Server                │
│  ┌────────────────────────────────────────────────┐ │
│  │  Guardrails Flow                               │ │
│  │  1. User Input                                 │ │
│  │  2. Check with Local Models                   │ │
│  │     ├─► Jailbreak Detector (BERT)            │ │
│  │     ├─► Toxicity Detector (BERT)             │ │
│  │     └─► Custom Models                         │ │
│  │  3. LLM Generation (if safe)                  │ │
│  │  4. Output Guardrails                         │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
# Install with local model support
pip install nemo-guardrails-cai[local-models]

# Or install manually
pip install transformers torch sentencepiece
```

### 2. Configure Local Models

Create a server configuration file with local models:

```yaml
# server_config.yaml
config_path: config

server:
  host: 0.0.0.0
  port: 8080

llm:
  provider: openai
  model: gpt-3.5-turbo

# Local models configuration
local_models:
  # Jailbreak detection
  jailbreak_detector:
    type: huggingface
    model_name: "protectai/deberta-v3-base-prompt-injection-v2"
    device: cpu  # or 'cuda' for GPU
    task_type: classification
    labels: ["safe", "jailbreak"]
    threshold: 0.7
    auto_load: true

  # Toxicity detection
  toxicity_detector:
    type: huggingface
    model_name: "unitary/toxic-bert"
    device: cpu
    task_type: classification
    labels: ["non-toxic", "toxic"]
    threshold: 0.5
    auto_load: true
```

### 3. Create Guardrails Configuration

Define flows that use local models:

```colang
# config/rails/local_checks.co

define bot inform jailbreak detected
  "I cannot respond to that type of request."

define bot inform toxic content detected
  "Please rephrase your message respectfully."

# Check for jailbreak attempts
define flow check jailbreak with local model
  user ...
  $is_jailbreak = execute check_jailbreak_local

  if $is_jailbreak
    bot inform jailbreak detected
    stop

# Check for toxic content
define flow check toxicity with local model
  user ...
  $is_toxic = execute check_toxicity_local

  if $is_toxic
    bot inform toxic content detected
    stop
```

```yaml
# config/config.yml
models:
  - type: main
    engine: openai
    model: gpt-3.5-turbo

rails:
  input:
    flows:
      - check jailbreak with local model
      - check toxicity with local model
```

### 4. Start the Server

```bash
# Start with configuration
nemo-guardrails-server --config server_config.yaml

# Or in CAI (port auto-detected)
python app.py
```

## Available Models

### Pre-trained Models

#### Jailbreak Detection

```yaml
jailbreak_detector:
  type: huggingface
  model_name: "protectai/deberta-v3-base-prompt-injection-v2"
  device: cpu
  labels: ["safe", "injection"]
  threshold: 0.7
```

**Alternative models:**
- `deepset/deberta-v3-base-injection`
- Custom fine-tuned models

#### Toxicity Detection

```yaml
toxicity_detector:
  type: huggingface
  model_name: "unitary/toxic-bert"
  device: cpu
  labels: ["non-toxic", "toxic"]
  threshold: 0.5
```

**Alternative models:**
- `martin-ha/toxic-comment-model`
- `unitary/multilingual-toxic-xlm-roberta`

#### Sentiment Analysis

```yaml
sentiment_analyzer:
  type: huggingface
  model_name: "distilbert-base-uncased-finetuned-sst-2-english"
  device: cpu
  labels: ["negative", "positive"]
  threshold: 0.6
```

### Custom Fine-Tuned Models

You can use your own fine-tuned models:

```yaml
custom_classifier:
  type: huggingface
  model_name: "/home/cdsw/models/my-custom-bert"  # Local path
  device: cuda
  labels: ["safe", "unsafe", "suspicious"]
  threshold: 0.8
```

## Configuration Options

### Model Configuration

```yaml
model_name:
  type: huggingface              # Model service type
  model_name: "model-org/model"  # HuggingFace model or local path
  device: cpu                    # cpu, cuda, or mps
  task_type: classification      # Task type (classification, ner, etc.)
  labels: ["safe", "unsafe"]     # Label names in order
  threshold: 0.7                 # Classification threshold (0-1)
  batch_size: 1                  # Batch size for inference
  max_length: 512                # Maximum sequence length
  use_fast_tokenizer: true       # Use fast tokenizer (default: true)
  auto_load: true                # Load on server startup (default: true)
```

### Device Selection

**CPU (Default)**
```yaml
device: cpu
```
- Works everywhere
- Good for small models and low-throughput scenarios

**GPU (Recommended for Production)**
```yaml
device: cuda
```
- Requires CUDA-enabled GPU
- 5-10x faster than CPU
- Recommended for high-throughput deployments

**Apple Silicon (MPS)**
```yaml
device: mps
```
- For Apple M1/M2/M3 chips
- 3-5x faster than CPU on Mac

## Custom Actions

Three custom actions are available in Colang flows:

### 1. check_jailbreak_local

```colang
define flow
  user ...
  $is_jailbreak = execute check_jailbreak_local

  if $is_jailbreak
    bot refuse to respond
    stop
```

Uses the `jailbreak_detector` model from registry.

### 2. check_toxicity_local

```colang
define flow
  user ...
  $is_toxic = execute check_toxicity_local

  if $is_toxic
    bot refuse to respond
    stop
```

Uses the `toxicity_detector` model from registry.

### 3. check_with_local_model (Generic)

```colang
define flow
  user ...
  $result = execute check_with_local_model(model_name="custom_model")

  if not $result.is_safe
    bot refuse to respond
    stop
```

Can use any registered model. Returns a dictionary with:
- `is_safe`: Boolean
- `score`: Confidence score (0-1)
- `label`: Predicted label

## Deployment in CAI

### Option 1: Embedded Models (Recommended)

Models run within the guardrails server process:

```yaml
# server_config.yaml
local_models:
  jailbreak_detector:
    type: huggingface
    model_name: "protectai/deberta-v3-base-prompt-injection-v2"
    auto_load: true
```

**Pros:**
- Simple deployment
- Low latency
- No additional services

**Cons:**
- Shares resources with main server
- Models loaded once

### Option 2: Separate Model Service

Run models as a separate CAI Application:

```bash
# Start model service on separate port
python model_service.py \
  --model "unitary/toxic-bert" \
  --model-name toxicity_detector \
  --device cuda \
  --port 8081
```

Then configure guardrails to use the service via HTTP API.

**Pros:**
- Independent scaling
- Can restart models without affecting guardrails
- Better resource isolation

**Cons:**
- More complex deployment
- Network latency

## Performance Optimization

### Model Selection

**Small Models (Recommended for CPU)**
- `distilbert-*` models (~66M parameters)
- Inference: 20-50ms per request
- Memory: ~250MB

**Medium Models**
- `bert-base-*` models (~110M parameters)
- Inference: 50-100ms per request
- Memory: ~440MB

**Large Models**
- `bert-large-*` models (~340M parameters)
- Inference: 150-300ms per request
- Memory: ~1.3GB

### Batch Processing

```yaml
batch_size: 8  # Process multiple requests together
```

Increases throughput but adds latency for individual requests.

### GPU Acceleration

```yaml
device: cuda
```

Requirements:
- NVIDIA GPU with CUDA support
- `torch` with CUDA enabled
- Sufficient GPU memory (2GB+ recommended)

## Monitoring

### Health Check

```bash
curl http://localhost:8080/health
```

Returns model status:

```json
{
  "status": "healthy",
  "models": {
    "jailbreak_detector": {
      "loaded": true,
      "model_name": "protectai/deberta-v3-base-prompt-injection-v2",
      "device": "cpu"
    }
  }
}
```

### Logging

Models log key events:

```
INFO - Loading HuggingFace model: protectai/deberta-v3-base-prompt-injection-v2
INFO - Using CPU device
INFO - Model loaded successfully on -1
INFO - Checking for jailbreak: Ignore previous instructions...
INFO - Jailbreak check result: {'label': 'jailbreak', 'score': 0.95, 'is_safe': False}
```

## Troubleshooting

### Model Not Loading

**Error:** `Model not found in registry`

**Solution:** Check model is configured in `local_models` section and `auto_load: true`.

### Out of Memory

**Error:** `CUDA out of memory` or `RuntimeError: [Errno 12] Cannot allocate memory`

**Solutions:**
1. Use smaller model (e.g., distilbert instead of bert-large)
2. Reduce `batch_size` to 1
3. Switch to CPU: `device: cpu`
4. Reduce `max_length` to 256 or 128

### Slow Inference

**CPU Performance:**
- Use distilled models (`distilbert-*`)
- Enable fast tokenizer: `use_fast_tokenizer: true`
- Consider upgrading to GPU

**GPU Not Being Used:**
- Check CUDA availability: `torch.cuda.is_available()`
- Verify correct PyTorch installation: `pip install torch --index-url https://download.pytorch.org/whl/cu118`

### Import Errors

**Error:** `No module named 'transformers'`

**Solution:**
```bash
pip install nemo-guardrails-cai[local-models]
```

## Example: Complete Setup

See [examples/server_config_with_local_models.yaml](../examples/server_config_with_local_models.yaml) for a complete configuration example.

## Best Practices

1. **Start with CPU**: Test on CPU first, then optimize with GPU if needed
2. **Monitor Performance**: Track latency and throughput in production
3. **Use Appropriate Thresholds**: Tune threshold values based on your use case
4. **Version Control Models**: Use specific model versions/commits in production
5. **Pre-download Models**: Download models during deployment, not at runtime
6. **Resource Allocation**: Allocate sufficient CPU/memory in CAI workspace

## Next Steps

- [Examples](../examples/config_with_local_models/) - Working configurations
- [Model Service](../model_service.py) - Standalone model service
- [Custom Models](CUSTOM_MODELS.md) - Training your own models

## Support

For issues or questions:
- [GitHub Issues](https://github.com/cloudera/nemo-guardrails-cai/issues)
- [Discussions](https://github.com/cloudera/nemo-guardrails-cai/discussions)
