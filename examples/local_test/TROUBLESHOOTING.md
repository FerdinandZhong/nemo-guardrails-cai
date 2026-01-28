# Troubleshooting Local Testing

Common issues and solutions when testing NeMo Guardrails locally.

## Error: "self_check_input prompt template missing"

### Symptom
```
ValidationError: You must provide a `self_check_input` prompt template.
```

### Cause
The `self check input` and `self check output` rails require prompt templates that define how the LLM should evaluate content.

### Solution
Ensure you have a `prompts.yml` file in the same directory as `config.yml`:

```yaml
# prompts.yml
prompts:
  - task: self_check_input
    content: |
      Your task is to check if the user message below complies with the company policy.

      User message: "{{ user_input }}"

      Question: Should the user message be blocked (Yes or No)?
      Answer:

  - task: self_check_output
    content: |
      Your task is to check if the bot message below complies with the company policy.

      Bot message: "{{ bot_response }}"

      Question: Should the message be blocked (Yes or No)?
      Answer:
```

✅ **Fixed** - The `prompts.yml` file is now included in `examples/local_test/`

---

## Error: "No request config_ids provided and server has no default configuration"

### Symptom
```
GuardrailsConfigurationError: No request config_ids provided and server has no default configuration
```

### Cause
The FastAPI server needs to know which configuration to use when receiving API requests.

### Solution
The server needs proper configuration with:
- `rails_config_path`: Path to config directory
- `single_config_mode`: Set to `True`
- `single_config_id`: Config ID for validation
- Cached rails instance with empty string key

```python
app.rails_config_path = str(config_path)
app.single_config_mode = True
app.single_config_id = "local_test"

from nemoguardrails.server.api import llm_rails_instances
llm_rails_instances[""] = rails  # Empty string key for single config mode
```

✅ **Fixed** - The `test_server.py` now properly configures the server

---

## Error: "Invalid configuration ids: ['local_test']"

### Symptom
```
ValueError: Invalid configuration ids: ['local_test']
```

### Cause
In single config mode, the API validates that incoming config_ids match `app.single_config_id`. This error means:
1. `single_config_mode` is True
2. Request has a config_id
3. The config_id doesn't match `app.single_config_id`

### Solution
Make sure the `single_config_id` is set correctly:

```python
app.single_config_id = "local_test"  # Must match what client sends
```

For the OpenAI-compatible endpoint, requests typically don't include a config_id, so the server uses the default. The validation happens in `_get_rails()`:

```python
if app.single_config_mode:
    if config_ids != [app.single_config_id]:
        raise ValueError(f"Invalid configuration ids: {config_ids}")
    config_ids = [""]  # Use empty string for path joining
```

✅ **Fixed** - The server now properly validates config IDs

---

## Error: "OPENAI_API_KEY not set"

### Symptom
Server refuses to start with:
```
❌ OPENAI_API_KEY not set!
Please set it: export OPENAI_API_KEY='your-key-here'
```

### Cause
The default rails use OpenAI's API to check content, so an API key is required.

### Solution

**Option 1: Direct export**
```bash
export OPENAI_API_KEY='sk-proj-your-key-here'
```

**Option 2: Use .env file**
```bash
cp examples/local_test/.env.example examples/local_test/.env
# Edit .env and add your key
export $(cat examples/local_test/.env | grep -v '^#' | xargs)
```

**Option 3: Use setup script**
```bash
./examples/local_test/setup_env.sh
```

Get your API key from: https://platform.openai.com/api-keys

---

## Error: "NeMo Guardrails not installed"

### Symptom
```
ImportError: No module named 'nemoguardrails'
```

### Cause
NeMo Guardrails package is not installed in your Python environment.

### Solution

**With conda environment:**
```bash
conda activate vllm-playground-env
pip install nemoguardrails
```

**Without conda:**
```bash
pip install nemoguardrails
```

**Verify installation:**
```bash
python -c "import nemoguardrails; print(nemoguardrails.__version__)"
```

✅ **Note** - The `vllm-playground-env` already has nemoguardrails 0.19.0 installed

---

## Warning: "No config_id or config_ids provided, using default config_id"

### Symptom
```
UserWarning: No config_id or config_ids provided, using default config_id
```

### Cause
This is a **normal warning** when using the OpenAI-compatible endpoint (`/v1/chat/completions`). The client doesn't send a config_id, so the server uses the default.

### Is this a problem?
**No!** This is expected behavior. The warning just informs you that the server is using the default configuration.

### If you want to suppress it
The warning is informational and doesn't indicate an error. It's generated in the API code to help with debugging.

---

## Server Starts but Chat UI Shows "abc" and "hello_world"

### Symptom
Opening http://localhost:8080 shows a dropdown with "abc" and "hello_world" instead of your custom config.

### Cause
Server is running in **multi-config mode** instead of single-config mode.

### Solution
Ensure `test_server.py` has:
```python
app.single_config_mode = True
app.single_config_id = "local_test"
```

✅ **Fixed** - The server now runs in single-config mode

---

## Cannot Connect to Server

### Symptom
```
Connection refused
```
or
```
Failed to connect to localhost:8080
```

### Cause
Server is not running or is on a different port.

### Solution

1. **Check if server is running:**
   ```bash
   lsof -i :8080
   ```

2. **Start the server:**
   ```bash
   export OPENAI_API_KEY='your-key'
   ./examples/local_test/run_with_conda.sh
   ```

3. **Check the server output for actual port:**
   The server logs will show:
   ```
   🚀 Starting server on http://localhost:8080
   ```

4. **Make sure you're in the right directory:**
   ```bash
   cd /Users/zhongqishuai/Projects/cldr_projects/nemo-guardrails-cai
   ```

---

## Test Client Fails

### Symptom
```python
❌ ERROR: [Errno 61] Connection refused
```

### Cause
Server is not running when the test client tries to connect.

### Solution
Always start the server FIRST in one terminal, then run the client in another terminal.

**Terminal 1:**
```bash
export OPENAI_API_KEY='your-key'
./examples/local_test/run_with_conda.sh
```

**Terminal 2:**
```bash
export OPENAI_API_KEY='your-key'
./examples/local_test/run_with_conda.sh python examples/local_test/test_client.py
```

---

## Configuration Changes Not Taking Effect

### Symptom
You modified `config.yml` or `prompts.yml` but the changes don't appear.

### Cause
The server caches the configuration. Changes require a restart.

### Solution
1. Stop the server (Ctrl+C)
2. Restart the server
3. Test again

The rails instance is loaded once at startup and cached in memory.

---

## Slow Response Times

### Symptom
Each request takes 2-3 seconds or more.

### Cause
The default rails use OpenAI's API for:
1. Input checking (~1 second)
2. Main generation (~1 second)
3. Output checking (~1 second)

Total: ~3 seconds per request

### Is this normal?
**Yes!** This is expected with the default rails that use LLM-based checking.

### How to speed it up
Consider using local models for checking instead:
- See: `examples/config_with_local_models/`
- Local BERT models can check in ~50ms instead of ~1s
- Reduces latency from 3s to ~1.1s
- Reduces cost by ~90%

---

## High API Costs

### Symptom
OpenAI API costs are higher than expected.

### Cause
Each request makes 3 API calls:
- Input check: ~$0.0005
- Main generation: ~$0.002
- Output check: ~$0.0005
Total: ~$0.003 per request

### Solution
Switch to local models for checking:
- Reduces to 1 API call (main generation only)
- Saves ~$0.001 per request (67% reduction)
- See: `docs/LOCAL_MODELS.md`

---

## Conda Environment Issues

### Symptom
```
Conda environment 'vllm-playground-env' not found
```

### Cause
The conda environment doesn't exist or has a different name.

### Solution

1. **List available environments:**
   ```bash
   conda env list
   ```

2. **Use the correct environment name:**
   Edit `run_with_conda.sh` and change:
   ```bash
   CONDA_ENV="your-actual-env-name"
   ```

3. **Or activate manually:**
   ```bash
   conda activate your-actual-env-name
   python examples/local_test/test_server.py
   ```

---

## Getting Help

If you encounter an issue not covered here:

1. **Check the logs** - The server prints detailed error messages
2. **Verify prerequisites** - OPENAI_API_KEY set, nemoguardrails installed
3. **Check file locations** - Make sure `config.yml` and `prompts.yml` exist
4. **Review documentation** - See other .md files in this directory

**Useful documentation:**
- [QUICKSTART_CONDA.md](QUICKSTART_CONDA.md) - Quick start guide
- [UNDERSTANDING_CONFIGS.md](UNDERSTANDING_CONFIGS.md) - Config structure
- [CONDA_SETUP.md](CONDA_SETUP.md) - Conda environment setup
- [ENV_SETUP.md](ENV_SETUP.md) - Environment variables

---

## Quick Diagnostic Commands

Run these to check your setup:

```bash
# Check conda environment
conda env list | grep vllm-playground-env

# Check nemoguardrails
conda run -n vllm-playground-env python -c "import nemoguardrails; print(nemoguardrails.__version__)"

# Check API key
echo $OPENAI_API_KEY

# Check files exist
ls examples/local_test/config.yml examples/local_test/prompts.yml

# Check if server is running
lsof -i :8080

# Test OpenAI connection
conda run -n vllm-playground-env python -c "from openai import OpenAI; import os; c = OpenAI(api_key=os.environ.get('OPENAI_API_KEY')); print(c.chat.completions.create(model='gpt-3.5-turbo', messages=[{'role':'user','content':'hi'}], max_tokens=5))"
```

All commands should complete successfully if your setup is correct.
