# Quick Start with Conda Environment

Get started testing NeMo Guardrails locally in 2 minutes!

## Prerequisites

- ✅ Conda environment `vllm-playground-env` (already set up)
- ✅ NeMo Guardrails 0.19.0 (already installed)
- ⚠️ OpenAI API key (you need to provide this)

## Step 1: Set Your API Key

```bash
export OPENAI_API_KEY='sk-proj-your-actual-key-here'
```

Get your API key from: https://platform.openai.com/api-keys

## Step 2: Start the Server

Open a terminal and run:

```bash
./examples/local_test/run_with_conda.sh
```

You should see:

```
======================================================================
Starting NeMo Guardrails Server (Local Test)
======================================================================
✅ Guardrails initialized
   Model: gpt-3.5-turbo
   Engine: openai

🚀 Starting server on http://localhost:8080
   Config: Local Test (examples/local_test/config.yml)
   Mode: Single Config
   OpenAI-compatible endpoint: http://localhost:8080/v1
   Chat UI: http://localhost:8080

Test with:
   python examples/local_test/test_client.py
   Or open http://localhost:8080 in your browser

Press Ctrl+C to stop
======================================================================
```

**Note:** The server runs in "single config mode" - it uses ONLY your custom configuration. You won't see the default "abc" or "hello_world" example bots. See [UNDERSTANDING_CONFIGS.md](UNDERSTANDING_CONFIGS.md) for details.

## Step 3: Test the Server

Open **another terminal** and run:

```bash
export OPENAI_API_KEY='sk-proj-your-actual-key-here'
./examples/local_test/run_with_conda.sh python examples/local_test/test_client.py
```

You'll see test results:

```
🧪 Testing NeMo Guardrails with Default Rails
======================================================================

Test 1/6: Normal Query
✅ PASS - Correctly allowed

Test 2/6: Jailbreak Attempt #1
✅ PASS - Correctly blocked

...

📊 Test Summary
Tests Passed: 6/6
🎉 All tests passed!
```

## Alternative: Activate Environment First

If you prefer to activate the environment:

```bash
# Terminal 1
conda activate vllm-playground-env
export OPENAI_API_KEY='your-key'
python examples/local_test/test_server.py
```

```bash
# Terminal 2
conda activate vllm-playground-env
export OPENAI_API_KEY='your-key'
python examples/local_test/test_client.py
```

## Test with curl

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "What is Python?"}]
  }'
```

## Troubleshooting

### Error: "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY='sk-proj-your-key-here'
```

### Error: "self_check_input prompt template missing"
The `prompts.yml` file is already created. If missing, check that you're in the project root directory.

### Server won't start
Make sure you're running from the project root:
```bash
cd /Users/zhongqishuai/Projects/cldr_projects/nemo-guardrails-cai
```

## What Gets Tested

- ✅ Normal queries pass through (e.g., "What is Python?")
- ✅ Jailbreak attempts are blocked (e.g., "Ignore all instructions...")
- ✅ Technical questions work normally
- ✅ Educational questions work normally

## Testing with the Chat UI

The server includes a web-based chat interface:

1. Start the server (as shown above)
2. Open http://localhost:8080 in your browser
3. Type messages to test the guardrails interactively
4. Try jailbreak attempts to see them get blocked in real-time!

## Files Created

I've created these files for you:

1. **[prompts.yml](prompts.yml)** - Defines how LLM checks inputs/outputs (REQUIRED)
2. **[run_with_conda.sh](run_with_conda.sh)** - Helper script to run with conda
3. **[CONDA_SETUP.md](CONDA_SETUP.md)** - Detailed conda environment guide
4. **[UNDERSTANDING_CONFIGS.md](UNDERSTANDING_CONFIGS.md)** - Explains where "abc" and "hello_world" come from

The existing files:
- **config.yml** - Guardrails configuration
- **test_server.py** - Test server (updated for single-config mode)
- **test_client.py** - Automated tests
- **.env.example** - Environment variable template

## Ready to Test!

You're all set! Just run:

```bash
# Terminal 1
export OPENAI_API_KEY='your-key'
./examples/local_test/run_with_conda.sh

# Terminal 2
export OPENAI_API_KEY='your-key'
./examples/local_test/run_with_conda.sh python examples/local_test/test_client.py
```

🚀 That's it!
