#!/usr/bin/env python3
"""
Diagnostic script to check NeMo Guardrails configuration.
"""

import os
from pathlib import Path

# Set API key for imports
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-test"

print("=" * 70)
print("NeMo Guardrails Configuration Diagnostic")
print("=" * 70)
print()

# 1. Check NeMo Guardrails version
print("1. NeMo Guardrails Version:")
try:
    import nemoguardrails
    print(f"   ✅ Version: {nemoguardrails.__version__}")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# 2. Check config file
print("2. Configuration Files:")
config_path = Path(__file__).parent / "config.yml"
prompts_path = Path(__file__).parent / "prompts.yml"
print(f"   config.yml exists: {config_path.exists()}")
print(f"   prompts.yml exists: {prompts_path.exists()}")
print()

# 3. Check if configs can be loaded
print("3. Loading Rails Configuration:")
try:
    from nemoguardrails import RailsConfig
    rails_config = RailsConfig.from_path(str(config_path.parent))
    print(f"   ✅ Config loaded successfully")
    print(f"      Models: {[m.model for m in rails_config.models]}")
    print(f"      Input rails: {rails_config.rails.input.flows if rails_config.rails.input else 'None'}")
    print(f"      Output rails: {rails_config.rails.output.flows if rails_config.rails.output else 'None'}")
except Exception as e:
    print(f"   ❌ Error loading config: {e}")
    import traceback
    traceback.print_exc()
print()

# 4. Check app configuration
print("4. NeMo Guardrails Server App:")
try:
    from nemoguardrails.server import api
    print(f"   api.app type: {type(api.app).__name__}")
    print(f"   api.app.default_config_id: {api.app.default_config_id}")
    print(f"   api.app.single_config_mode: {api.app.single_config_mode}")
    print(f"   api.app.single_config_id: {api.app.single_config_id}")
    print(f"   api.app.rails_config_path: {api.app.rails_config_path}")
    print(f"   api.app.disable_chat_ui: {api.app.disable_chat_ui}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
print()

# 5. Check cached rails
print("5. Cached Rails Instances:")
try:
    from nemoguardrails.server.api import llm_rails_instances
    print(f"   llm_rails_instances type: {type(llm_rails_instances)}")
    print(f"   Keys: {list(llm_rails_instances.keys())}")
    print(f"   Number of cached instances: {len(llm_rails_instances)}")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# 6. Simulate what test_server.py does
print("6. Simulating test_server.py Setup:")
try:
    from nemoguardrails import RailsConfig, LLMRails
    from nemoguardrails.server import api
    from nemoguardrails.server.api import llm_rails_instances

    config_path = Path(__file__).parent
    config_id = "local_test"

    # Load config
    rails_config = RailsConfig.from_path(str(config_path))
    rails = LLMRails(rails_config)

    # Configure app
    app = api.app
    app.rails_config_path = str(config_path)
    app.single_config_mode = True
    app.single_config_id = config_id
    app.default_config_id = config_id

    # Cache rails
    cache_key = ""
    llm_rails_instances[cache_key] = rails

    print(f"   ✅ Setup simulation successful")
    print(f"      app.rails_config_path: {app.rails_config_path}")
    print(f"      app.single_config_mode: {app.single_config_mode}")
    print(f"      app.single_config_id: {app.single_config_id}")
    print(f"      app.default_config_id: {app.default_config_id}")
    print(f"      Cached with key: '{cache_key}'")
    print(f"      llm_rails_instances keys: {list(llm_rails_instances.keys())}")

except Exception as e:
    print(f"   ❌ Error during setup: {e}")
    import traceback
    traceback.print_exc()
print()

print("=" * 70)
print("Diagnostic Complete")
print("=" * 70)
