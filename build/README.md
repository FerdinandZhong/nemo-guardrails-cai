# Build System for NeMo Guardrails CAI Application

This directory contains build and deployment scripts for running NeMo Guardrails in Cloudera AI (CAI) environments.

## Overview

The build system provides:
- **Shell scripts** for environment setup and application startup
- **Python scripts** for CAI environment detection and coordination
- **Proper virtual environment handling** for both local and CAI deployments
- **Compatibility** with CAI's application deployment model

## Directory Structure

```
build/
├── README.md                    # This file
├── start_application.py        # Python entry point for starting the app
├── build_client.py            # Python entry point for building dependencies
└── shell_scripts/
    ├── start_application.sh    # Shell script to start NeMo Guardrails server
    └── build_client.sh         # Shell script to setup environment
```

## Files

### Shell Scripts

#### `shell_scripts/build_client.sh`
Sets up the Python environment:
- Creates virtual environment if needed
- Installs project dependencies from `pyproject.toml`
- Installs NeMo Guardrails
- Verifies installation

**Usage:**
```bash
bash build/shell_scripts/build_client.sh
```

#### `shell_scripts/start_application.sh`
Starts the NeMo Guardrails server:
- Activates virtual environment
- Sets environment variables
- Verifies configuration path
- Starts NeMo Guardrails server using CLI

**Environment Variables:**
- `GUARDRAILS_CONFIG_PATH` - Path to guardrails config (default: `examples/local_test`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `CDSW_APP_PORT` - Port (auto-detected by CAI, default: `8080`)

**Usage:**
```bash
bash build/shell_scripts/start_application.sh
```

### Python Scripts

#### `start_application.py`
Entry point for starting the application in CAI:
- Detects `IS_COMPOSABLE` environment variable (CAI detection)
- Sets project root appropriately
- Executes `start_application.sh`

**Features:**
- Works both locally and in CAI
- Handles project path management
- Proper logging

**Usage:**
```bash
python build/start_application.py
```

**Or from CAI:**
- CAI will automatically call this script
- Respects `IS_COMPOSABLE` environment variable

#### `build_client.py`
Entry point for building the project in CAI:
- Detects `IS_COMPOSABLE` environment variable
- Sets project root appropriately
- Executes `build_client.sh`

**Usage:**
```bash
python build/build_client.py
```

**Or from CAI:**
- CAI can call this during project setup
- Respects `IS_COMPOSABLE` environment variable

## How CAI Integration Works

### Local Development

1. **Setup environment:**
   ```bash
   python build/build_client.py
   ```

2. **Start application:**
   ```bash
   python build/start_application.py
   ```

### CAI Deployment

1. **Build Phase** (via Jobs):
   - CAI sets `IS_COMPOSABLE=true`
   - Calls `python build/build_client.py`
   - Creates virtual environment at `/home/cdsw/.venv`
   - Installs dependencies

2. **Application Launch** (via Application):
   - CAI creates an application
   - Application startup script calls `bash build/shell_scripts/start_application.sh`
   - Or Python calls `python build/start_application.py`
   - Server listens on `CDSW_APP_PORT` (auto-detected)

## Environment Variables

### During Build (build_client.sh)

No special variables needed. Uses default Python and pip.

### During Startup (start_application.sh)

```bash
# Configuration
GUARDRAILS_CONFIG_PATH=examples/local_test    # Path to config directory
LOG_LEVEL=INFO                                 # Logging level

# CAI Auto-detected
CDSW_APP_PORT=8080                            # Set automatically by CAI
```

### CAI-Specific (for Python scripts)

```bash
IS_COMPOSABLE=true    # Set by CAI to indicate composable/application environment
```

## Integration with cai_integration

The `cai_integration/launch_guardrails.py` script:
1. Reads configuration from `jobs_config.yaml`
2. Generates startup script using `_build_startup_script()`
3. Creates CAI Application with startup script
4. Monitors application startup

**Updated startup script now uses:**
```bash
python -m nemoguardrails server \
    --config "$GUARDRAILS_CONFIG_PATH" \
    --port "$CDSW_APP_PORT" \
    --verbose
```

This replaces the old manual `nemo_guardrails_cai.server` approach with the robust NeMo Guardrails CLI.

## Configuration

### Default Configuration Path

The system looks for configuration in this order:
1. `$GUARDRAILS_CONFIG_PATH` environment variable
2. `examples/config` (production default)
3. `examples/local_test` (fallback)

### Creating Configuration

For local testing:
```bash
# Config directory structure
examples/local_test/
├── config.yml          # Guardrails configuration
├── prompts.yml         # Prompt templates
└── rails/              # Custom rails (optional)
```

For production:
```bash
examples/config/
├── config.yml
├── prompts.yml
├── rails/              # Custom rails
└── kb/                 # Knowledge base (optional)
```

## Troubleshooting

### Build fails with "nemoguardrails not found"

**Solution:** Ensure pyproject.toml includes nemoguardrails in dependencies:
```toml
[project]
dependencies = [
    "nemoguardrails>=0.19.0",
    ...
]
```

Or install manually:
```bash
source .venv/bin/activate
pip install nemoguardrails
```

### Application starts but shows "no configuration found"

**Solution:** Verify config path:
```bash
# Check path exists
ls examples/local_test/config.yml

# Set explicitly
export GUARDRAILS_CONFIG_PATH=examples/local_test
```

### Port already in use

**Solution:** The `CDSW_APP_PORT` is set by CAI. For local testing, change port:
```bash
# Edit shell script or set environment
CDSW_APP_PORT=9090 bash build/shell_scripts/start_application.sh
```

### Virtual environment not created

**Solution:** Ensure Python 3.9+ is available:
```bash
python3 --version
python3 -m venv .venv
```

## Patterns Used

This build system follows the same patterns as:
- **CAI_AMP_Synthetic_Data_Studio** - Reference implementation
- **ray-serve-cai** - CAI deployment patterns
- **Standard CAI applications** - Python/shell script coordination

## Next Steps

1. **Local Testing:**
   ```bash
   python build/build_client.py
   python build/start_application.py
   ```

2. **CAI Integration:**
   - Use `cai_integration/` scripts to deploy to CAI
   - They reference these build scripts automatically

3. **Configuration:**
   - Customize `examples/config/` for your use case
   - Or use `examples/local_test/` for testing

## References

- [CAI Documentation](https://docs.cloudera.com/)
- [NeMo Guardrails Documentation](https://github.com/NVIDIA/NeMo-Guardrails)
- [AMP Projects Pattern](../CAI_AMP_Synthetic_Data_Studio/)
- [Local Testing Guide](../examples/local_test/QUICKSTART_CONDA.md)
- [CAI Integration Guide](../cai_integration/README.md)
