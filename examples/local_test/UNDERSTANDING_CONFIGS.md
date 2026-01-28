# Understanding NeMo Guardrails Configurations

## Where do "abc" and "hello_world" come from?

When you see "abc" and "hello_world" in the NeMo Guardrails UI, these are **built-in example configurations** that come with the NeMo Guardrails package itself.

### Location of Built-in Examples

These examples are installed with the package at:
```
<conda-env>/lib/python3.12/site-packages/nemoguardrails/examples/bots/
├── abc/                    # ABC Company employee handbook bot
│   ├── config.yml
│   ├── prompts.yml
│   ├── rails/
│   └── kb/
├── hello_world/            # Simple hello world bot
│   ├── config.yml
│   └── rails.co
└── abc_v2/                 # ABC Company bot (v2 syntax)
```

For your environment, they're at:
```
/Users/zhongqishuai/miniconda3/envs/vllm-playground-env/lib/python3.12/site-packages/nemoguardrails/examples/bots/
```

### What is the "abc" bot?

The "abc" bot is a demo bot that answers questions about a fictional "ABC Company" employee handbook. It includes:

- **Config**: Uses GPT-3.5-turbo-instruct
- **Rails**: Self check input and output
- **Knowledge Base**: Company policies (paid time off, etc.)
- **Purpose**: Demonstrates a typical enterprise use case

Example from abc/config.yml:
```yaml
instructions:
  - type: general
    content: |
      The bot is designed to answer employee questions about the ABC Company.
      The bot is knowledgeable about the employee handbook and company policies.

models:
  - type: main
    engine: openai
    model: gpt-3.5-turbo-instruct

rails:
  input:
    flows:
      - self check input
  output:
    flows:
      - self check output
```

### What is the "hello_world" bot?

The "hello_world" bot is the simplest possible example:

- **Config**: Minimal configuration
- **Rails**: Basic greeting flow
- **Purpose**: Quick start / learning

## Server Modes

NeMo Guardrails server can run in two modes:

### 1. Multi-Config Mode (Default)

Shows multiple bot configurations in the UI, including:
- Your custom configs (from `--config` path)
- Built-in examples (abc, hello_world)

This is what you see when the UI shows a dropdown with "abc" and "hello_world".

**When it happens:**
```python
# Server detects a directory with multiple config folders
# Each subfolder is treated as a separate bot config
```

### 2. Single-Config Mode (What We Want)

Uses only ONE specific configuration - your custom config.

**How to enable:**
```python
app.single_config_mode = True
app.rails = rails  # Your specific rails instance
```

This is what our updated `test_server.py` now does!

## Why You Were Seeing "abc"

Before the fix, the server was running in **multi-config mode** and showing:
1. Built-in examples from the package (abc, hello_world)
2. Your local config (if detected)

The dropdown in the UI let you switch between these configurations.

## After the Fix

Now the server runs in **single-config mode** and:
- ✅ Uses ONLY your config ([examples/local_test/config.yml](config.yml))
- ✅ Doesn't show "abc" or "hello_world" in dropdown
- ✅ Chat UI opens directly with your guardrails active

## How to Switch Between Modes

### Use Your Custom Config Only (Single Mode)
```bash
# In test_server.py (already done)
# Use the NeMo Guardrails CLI to start the server
nemoguardrails server --config /path/to/config --port 8080
```

**How it works:**
- The NeMo Guardrails CLI handles proper FastAPI app initialization
- Automatically loads the config directory
- Properly sets up all internal state management
- No manual configuration needed
- Much more reliable than manual FastAPI setup

This is the current setup! Much simpler and more reliable.

### Use Multiple Configs (Multi Mode)
```python
# To serve multiple configs, organize like this:
configs/
├── my_bot_1/
│   ├── config.yml
│   └── prompts.yml
├── my_bot_2/
│   ├── config.yml
│   └── prompts.yml

# Then point server to the configs/ directory
```

## Accessing the Chat UI

When the server is running:

1. **Open browser**: http://localhost:8080
2. **Single mode**: Goes directly to chat with your config
3. **Multi mode**: Shows dropdown to select bot (abc, hello_world, etc.)

## Command Line Options

When using the NeMo Guardrails CLI:

```bash
# Start with specific config (single mode)
nemoguardrails server --config examples/local_test

# Start with multiple configs (multi mode)
nemoguardrails server --config examples/

# Disable chat UI
nemoguardrails server --config examples/local_test --disable-chat-ui
```

## Summary

| What | Where | Purpose |
|------|-------|---------|
| **"abc"** | Package examples | Demo bot for ABC Company employee handbook |
| **"hello_world"** | Package examples | Simplest possible bot example |
| **Your config** | `examples/local_test/` | Your custom guardrails configuration |
| **Single mode** | `app.single_config_mode = True` | Use ONLY your config |
| **Multi mode** | Default behavior | Show multiple configs in dropdown |

## Our Test Setup

Location: `examples/local_test/`

Files:
- [config.yml](config.yml) - Our custom configuration
- [prompts.yml](prompts.yml) - Self-check prompt templates
- [test_server.py](test_server.py) - Server in single-config mode (✅ Fixed!)

The server now uses **single-config mode** so you won't see "abc" or "hello_world" anymore - just your custom configuration!

## Verifying Single Config Mode

Start the server:
```bash
export OPENAI_API_KEY='your-key'
./examples/local_test/run_with_conda.sh
```

You should see:
```
✅ Guardrails initialized
   Model: gpt-3.5-turbo
   Engine: openai

🚀 Starting server on http://localhost:8080
   Config: Local Test (examples/local_test/config.yml)
   Mode: Single Config  ← This confirms single mode!
   Chat UI: http://localhost:8080
```

Then open http://localhost:8080 in your browser - you'll go straight to chat with YOUR config, no "abc" or "hello_world" dropdown!
