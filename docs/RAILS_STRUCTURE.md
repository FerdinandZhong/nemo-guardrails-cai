# NeMo Guardrails Structure and Default Rails

This guide explains where default rails are located and how the NeMo Guardrails configuration system works.

## Directory Structure

### Your Project Configuration

When you use NeMo Guardrails, you create a configuration directory (typically called `config/`) in your project:

```
your-project/
├── config/                          # Your guardrails configuration
│   ├── config.yml                   # Main configuration file
│   ├── prompts.yml                  # Custom prompts (optional)
│   └── rails/                       # Your custom rails
│       ├── topical.co               # Topical rails (Colang)
│       ├── moderation.co            # Moderation rails (Colang)
│       └── custom_checks.co         # Custom checks
└── server_config.yaml               # Server configuration
```

### NeMo Guardrails Library

Default/built-in rails are located in the NeMo Guardrails Python package:

```
nemoguardrails/                      # Installed Python package
├── rails/                           # Built-in rails library
│   ├── llm/                         # LLM-based rails
│   │   ├── self_check_input/        # Input checking
│   │   ├── self_check_output/       # Output checking
│   │   └── self_check_facts/        # Fact checking
│   └── ...
├── actions/                         # Built-in actions
│   ├── llm/                         # LLM actions
│   └── ...
└── library/                         # Standard library
    └── ...
```

## Default Rails

NeMo Guardrails comes with several built-in rails that you can reference in your configuration:

### 1. Self Check Input

**Location:** Built into NeMo Guardrails library

**Purpose:** Checks user input for jailbreaks, off-topic content, etc.

**Usage in config.yml:**
```yaml
rails:
  input:
    flows:
      - self check input
```

**How it works:**
- Uses an LLM to analyze user input
- Checks for prompt injection attempts
- Validates input is appropriate and on-topic
- Built-in prompt templates are in the NeMo library

### 2. Self Check Output

**Location:** Built into NeMo Guardrails library

**Purpose:** Checks LLM output before returning to user

**Usage in config.yml:**
```yaml
rails:
  output:
    flows:
      - self check output
```

**How it works:**
- Analyzes LLM response for issues
- Checks for harmful content
- Validates response appropriateness
- Can rewrite or block problematic outputs

### 3. Self Check Facts

**Location:** Built into NeMo Guardrails library

**Purpose:** Fact-checks LLM outputs against knowledge base

**Usage in config.yml:**
```yaml
rails:
  output:
    flows:
      - self check facts
```

**How it works:**
- Compares LLM response to provided context
- Identifies potential hallucinations
- Can trigger regeneration if facts are incorrect

### 4. Check Jailbreak

**Location:** Built-in action in NeMo Guardrails

**Purpose:** Detects jailbreak attempts

**Usage in your rails:**
```colang
define flow
  user ...
  $is_jailbreak = execute check_jailbreak

  if $is_jailbreak
    bot refuse to respond
    stop
```

**Note:** This is the default LLM-based check. With our local model implementation, you can use:
```colang
$is_jailbreak = execute check_jailbreak_local
```

## How Rails Are Loaded

### 1. Built-in Rails (Default)

When you reference a built-in rail like `self check input`, NeMo Guardrails:

1. Looks in its internal library (`nemoguardrails/rails/`)
2. Loads the pre-defined Colang flows
3. Uses built-in prompt templates
4. Applies the rail to your configuration

You **don't need to define** these rails - they're already in the library.

### 2. Your Custom Rails

When you create custom rails in your `config/rails/` directory:

1. NeMo Guardrails scans your config directory
2. Loads all `.co` (Colang) files from `config/rails/`
3. Merges your custom flows with built-in flows
4. Your custom rails can override or extend built-in ones

## Configuration Hierarchy

```
Your config.yml
    ↓
References flows (e.g., "self check input")
    ↓
NeMo checks: Is it a built-in flow?
    ├─ YES → Uses built-in from library
    └─ NO  → Looks in your config/rails/*.co files
```

## Example: Complete Configuration

### Your config/config.yml

```yaml
# Define the main LLM
models:
  - type: main
    engine: openai
    model: gpt-3.5-turbo

# Use both built-in and custom rails
rails:
  # Input rails
  input:
    flows:
      - self check input              # Built-in (from NeMo library)
      - check jailbreak with local    # Custom (from your config/rails/)
      - check toxic content           # Custom (from your config/rails/)

  # Output rails
  output:
    flows:
      - self check output             # Built-in (from NeMo library)
      - self check facts              # Built-in (from NeMo library)
      - check response safety         # Custom (from your config/rails/)
```

### Your config/rails/custom_checks.co

```colang
# Custom flow using local models
define flow check jailbreak with local
  user ...
  $is_jailbreak = execute check_jailbreak_local

  if $is_jailbreak
    bot refuse to respond
    stop

# Custom flow for toxic content
define flow check toxic content
  user ...
  $is_toxic = execute check_toxicity_local

  if $is_toxic
    bot inform content not allowed
    stop

define bot inform content not allowed
  "I cannot respond to that type of content."
```

## Where Do Custom Actions Go?

### Built-in Actions

Built-in actions like `check_jailbreak`, `retrieve_relevant_chunks`, etc. are in:
```
nemoguardrails/actions/
```

### Your Custom Actions (Python)

For complex custom actions, create an `actions.py` file in your config directory:

```
config/
├── config.yml
├── actions.py              # Your custom Python actions
└── rails/
    └── custom.co
```

**Example actions.py:**
```python
# config/actions.py
async def my_custom_check(context=None):
    """Custom action implemented in Python."""
    user_message = context.get("user_message", "")

    # Your custom logic here
    is_safe = your_validation_logic(user_message)

    return is_safe
```

**Register in config.yml:**
```yaml
actions:
  - my_custom_check
```

### With Our Local Model System

Our implementation automatically registers custom actions:

```python
# Already registered by nemo_guardrails_cai
- check_jailbreak_local
- check_toxicity_local
- check_with_local_model
```

These are available immediately in your Colang flows without additional registration.

## Overriding Default Rails

You **can override** default rails by defining your own with the same name:

### Example: Custom "self check input"

**config/rails/override.co:**
```colang
# Override the default "self check input" flow
define flow self check input
  user ...

  # Your custom implementation
  $is_safe = execute my_custom_input_checker

  if not $is_safe
    bot refuse to respond
    stop
```

NeMo Guardrails will use **your** implementation instead of the default.

## Best Practices

### 1. Use Built-in Rails When Possible

Built-in rails are:
- ✅ Well-tested
- ✅ Optimized
- ✅ Maintained by NVIDIA team

### 2. Add Custom Rails for Specific Needs

Create custom rails when you need:
- Domain-specific checks
- Local model integration (like our jailbreak detector)
- Custom business logic
- Specialized validation

### 3. Name Custom Flows Clearly

```colang
# Good: Descriptive names
define flow check medical terminology
define flow validate insurance claim
define flow check jailbreak with local model

# Avoid: Generic names that might conflict
define flow check  # Too generic
define flow validate  # Too generic
```

### 4. Organize by Purpose

```
config/rails/
├── input_checks.co      # All input validation
├── output_checks.co     # All output validation
├── topical.co           # Topic management
└── local_models.co      # Local model checks
```

## Viewing Loaded Rails

To see what rails are loaded, enable verbose logging:

```yaml
# config.yml
server:
  log_level: DEBUG
```

NeMo Guardrails will log:
```
DEBUG - Loading rails from: /path/to/config/rails/
DEBUG - Loaded flow: self check input (built-in)
DEBUG - Loaded flow: check jailbreak with local (custom)
```

## Summary

| Component | Location | Defined By |
|-----------|----------|------------|
| Built-in rails | `nemoguardrails/rails/` | NeMo Guardrails library |
| Your custom rails | `config/rails/*.co` | You |
| Built-in actions | `nemoguardrails/actions/` | NeMo Guardrails library |
| Your custom actions | `config/actions.py` | You |
| Our model actions | `nemo_guardrails_cai/actions/` | This package |
| Main config | `config/config.yml` | You |

## References

- [NeMo Guardrails GitHub](https://github.com/NVIDIA/NeMo-Guardrails)
- [Colang Language Guide](https://github.com/NVIDIA/NeMo-Guardrails/blob/main/docs/user_guides/colang-language-syntax-guide.md)
- [Configuration Guide](https://github.com/NVIDIA/NeMo-Guardrails/blob/main/docs/user_guides/configuration-guide.md)

## Next Steps

- [Local Models Guide](LOCAL_MODELS.md) - Use local models for checks
- [Examples](../examples/) - See working configurations
