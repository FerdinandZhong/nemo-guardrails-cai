# Using Conda Environment for Local Testing

This guide shows how to run local tests using the `vllm-playground-env` conda environment.

## Quick Start

### Option 1: Using the Helper Script (Easiest)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY='sk-proj-your-key-here'

# Start the server
./examples/local_test/run_with_conda.sh

# In another terminal, run tests
export OPENAI_API_KEY='sk-proj-your-key-here'
./examples/local_test/run_with_conda.sh python examples/local_test/test_client.py
```

### Option 2: Using conda run directly

```bash
# Set your OpenAI API key
export OPENAI_API_KEY='sk-proj-your-key-here'

# Start server
conda run -n vllm-playground-env python examples/local_test/test_server.py

# In another terminal, run tests
conda run -n vllm-playground-env python examples/local_test/test_client.py
```

### Option 3: Activate the environment

```bash
# Activate the environment
conda activate vllm-playground-env

# Set your API key
export OPENAI_API_KEY='sk-proj-your-key-here'

# Start server
python examples/local_test/test_server.py

# In another terminal (also activate the environment)
conda activate vllm-playground-env
python examples/local_test/test_client.py
```

## Environment Details

The `vllm-playground-env` conda environment already has:
- ✅ `nemoguardrails` (version 0.19.0)
- ✅ Python 3.12
- ✅ All required dependencies

## File Structure

The local test directory should have these files:

```
examples/local_test/
├── config.yml           # Guardrails configuration
├── prompts.yml         # Prompt templates for self-check rails
├── test_server.py      # Test server script
├── test_client.py      # Test client with scenarios
├── .env.example        # Environment variable template
├── setup_env.sh        # Interactive setup script
├── run_with_conda.sh   # Helper to run with conda (NEW)
├── ENV_SETUP.md        # Environment setup guide
└── README.md           # Main documentation
```

**Important:** The `prompts.yml` file is required! It defines how the LLM evaluates inputs and outputs for the self-check rails.

## Troubleshooting

### "OPENAI_API_KEY not set"

**Solution:** Export the environment variable before running:
```bash
export OPENAI_API_KEY='sk-proj-your-key-here'
```

Or load from .env file:
```bash
export $(cat examples/local_test/.env | grep -v '^#' | xargs)
```

### "self_check_input prompt template missing"

**Solution:** Make sure you have the `prompts.yml` file in the `examples/local_test/` directory. This file defines the prompt templates for the self-check rails.

### "Conda environment not found"

**Solution:** Check available environments:
```bash
conda env list
```

If you need to use a different environment, edit `run_with_conda.sh` and change the `CONDA_ENV` variable.

### "ImportError: No module named 'nemoguardrails'"

**Solution:** Install nemoguardrails in your conda environment:
```bash
conda activate vllm-playground-env
pip install nemoguardrails
```

## Testing Your Setup

### 1. Check conda environment

```bash
conda env list | grep vllm-playground-env
```

Should show: `vllm-playground-env`

### 2. Check nemoguardrails installation

```bash
conda run -n vllm-playground-env python -c "import nemoguardrails; print(nemoguardrails.__version__)"
```

Should print: `0.19.0` (or similar)

### 3. Check API key

```bash
echo $OPENAI_API_KEY
```

Should print your API key (starts with `sk-proj-` or `sk-`)

### 4. Check required files

```bash
ls examples/local_test/config.yml examples/local_test/prompts.yml
```

Both files should exist.

### 5. Start the server

```bash
export OPENAI_API_KEY='your-key'
./examples/local_test/run_with_conda.sh
```

Should see:
```
✅ Guardrails initialized
🚀 Starting server on http://localhost:8080
```

## Usage Examples

### Start server in background

```bash
export OPENAI_API_KEY='your-key'
./examples/local_test/run_with_conda.sh > server.log 2>&1 &
```

### Run tests

```bash
./examples/local_test/run_with_conda.sh python examples/local_test/test_client.py
```

### Manual testing with curl

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "What is Python?"}
    ]
  }'
```

### Run Python OpenAI client test

```bash
./examples/local_test/run_with_conda.sh python -c "
from openai import OpenAI
client = OpenAI(base_url='http://localhost:8080/v1', api_key='dummy')
response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[{'role': 'user', 'content': 'Hello!'}]
)
print(response.choices[0].message.content)
"
```

## Summary

**Easiest way to get started:**

```bash
# 1. Set API key
export OPENAI_API_KEY='sk-proj-your-key-here'

# 2. Start server
./examples/local_test/run_with_conda.sh

# 3. In another terminal, run tests
export OPENAI_API_KEY='sk-proj-your-key-here'
./examples/local_test/run_with_conda.sh python examples/local_test/test_client.py
```

Done! 🚀
