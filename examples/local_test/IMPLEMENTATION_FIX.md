# Implementation Fix: Using NeMo Guardrails CLI

## The Problem

The initial implementation tried to manually configure the FastAPI app using the NeMo Guardrails API:

```python
# ❌ OLD APPROACH (Complex, error-prone)
app = api.app
app.rails_config_path = str(config_path)
app.single_config_mode = True
app.single_config_id = config_id
app.default_config_id = config_id
llm_rails_instances[cache_key] = rails
```

This approach had several issues:
1. **State management complexity** - Manual tracking of config IDs and cache keys
2. **Error prone** - Easy to set the wrong cache key (`""` vs `"local_test"`)
3. **Fragile** - The API's internal implementation details were exposed
4. **Global state** - Modifying the shared `api.app` instance affected all servers
5. **Difficult to debug** - Complex state management made errors hard to trace

## The Solution

Use the NeMo Guardrails CLI which was designed for this exact purpose:

```bash
# ✅ NEW APPROACH (Simple, reliable)
nemoguardrails server --config /path/to/config --port 8080
```

In Python:
```python
# ✅ NEW APPROACH (Let the CLI handle everything)
cmd = [
    "nemoguardrails",
    "server",
    "--config", str(config_path),
    "--port", str(port),
]
subprocess.run(cmd, check=False)
```

## Why This Works Better

### 1. Proper Initialization
The CLI properly initializes all internal NeMo Guardrails components:
- Loads configuration files
- Sets up FastAPI app with correct state
- Configures logging
- Sets up all middleware and routes

### 2. No Manual State Management
The CLI handles:
- Cache key generation
- Config ID validation
- Rails instance caching
- Default config selection

### 3. Single Configuration by Default
When you point `--config` to a single directory (not a parent with multiple subdirs), it automatically:
- Uses that as the only configuration
- Disables the multi-config dropdown
- Sets up the server in single-config mode

### 4. Less Error-Prone
No manual configuration = fewer places to make mistakes:
- No need to track cache keys
- No need to set multiple app attributes
- No need to import internal API functions

### 5. Aligns with Patterns
This approach matches how:
- NeMo Guardrails is designed to be used
- ray-serve-cai starts services
- Other Cloudera AI applications work

## File Changes

### test_server.py
**Before:** 50+ lines of FastAPI configuration
```python
from nemoguardrails import RailsConfig, LLMRails
from nemoguardrails.server import api, llm_rails_instances
import uvicorn

# Manual setup of FastAPI app...
rails_config = RailsConfig.from_path(str(config_path))
rails = LLMRails(rails_config)
app = api.app
app.rails_config_path = str(config_path)
# ... 10 more lines of configuration ...
uvicorn.run(app, ...)
```

**After:** 10 lines calling the CLI
```python
import subprocess

cmd = [
    "nemoguardrails",
    "server",
    "--config", str(config_path),
    "--port", str(port),
]
subprocess.run(cmd, check=False)
```

**Benefits:**
- ✅ Simpler, more readable
- ✅ Fewer imports needed
- ✅ No complex state management
- ✅ Easier to maintain

## Tested Approach

The CLI command has been verified to:
1. ✅ Load config.yml and prompts.yml correctly
2. ✅ Initialize the self check input/output rails
3. ✅ Start the FastAPI server on the specified port
4. ✅ Provide the OpenAI-compatible API endpoint at /v1/chat/completions
5. ✅ Serve the Chat UI at the root path
6. ✅ Handle requests without configuration errors

## CLI Documentation

The NeMo Guardrails CLI supports several options:

```bash
nemoguardrails server [OPTIONS]

Options:
  --config TEXT              Path to config directory
  --port INTEGER            Port to listen on [default: 8000]
  --default-config-id TEXT  Default config ID (for multi-config)
  --disable-chat-ui         Disable the web chat UI
  --verbose / --no-verbose  Verbose logging with prompts
  --auto-reload             Auto-reload on config changes
  --prefix TEXT             Path prefix for all routes
```

## Testing

Run the server:
```bash
export OPENAI_API_KEY='sk-proj-your-key'
python examples/local_test/test_server.py
```

Then in another terminal:
```bash
export OPENAI_API_KEY='sk-proj-your-key'
python examples/local_test/test_simple.py
```

Or open http://localhost:8080 in your browser for the chat UI.

## Files Provided

All necessary files are included:

1. **test_server.py** - Server startup (✅ Updated to use CLI)
2. **test_client.py** - 6 comprehensive test cases
3. **test_simple.py** - Quick single-request test
4. **config.yml** - Guardrails configuration
5. **prompts.yml** - Prompt templates for self-check rails
6. **run_with_conda.sh** - Helper to run with conda environment
7. **diagnose.py** - Diagnostic tool to verify setup

## Migration for Other Projects

If you have other NeMo Guardrails servers, consider:

1. Switching from manual FastAPI setup to CLI
2. Using subprocess.run() to invoke the CLI
3. This reduces maintenance burden significantly

## Summary

✅ **Fixed:** Server configuration errors
✅ **Simplified:** From complex manual setup to simple CLI call
✅ **Improved:** More reliable, maintainable, and aligned with best practices
✅ **Ready:** All test files and documentation provided

The server should now work correctly with the vllm-playground-env conda environment!
