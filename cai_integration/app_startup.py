#!/usr/bin/env python3
"""
CAI Application Entry Point for NeMo Guardrails Server

This is the startup script for the CAI Application. It:
1. Activates the virtual environment
2. Configures the environment
3. Launches the bash startup script
4. Runs the NeMo Guardrails server

This script is set as the entry point when creating the CAI Application.
"""

import subprocess
import sys
import os
from pathlib import Path


def main():
    """Execute the application startup via bash wrapper."""
    project_root = Path("/home/cdsw")

    # Path to bash startup script (in cai_integration)
    bash_startup = project_root / "cai_integration" / "app_startup.sh"

    if not bash_startup.exists():
        print(f"❌ Error: Startup script not found at {bash_startup}")
        return 1

    print("=" * 70)
    print("🚀 NeMo Guardrails Application Startup")
    print("=" * 70)
    print(f"📝 Project root: {project_root}")
    print(f"📝 Executing: {bash_startup.name}\n")

    try:
        # Execute bash startup script
        result = subprocess.run(
            ["bash", str(bash_startup)],
            cwd=str(project_root),
            env={**os.environ, "PROJECT_ROOT": str(project_root)}
        )

        return result.returncode

    except Exception as e:
        print(f"\n❌ Error executing startup script: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
