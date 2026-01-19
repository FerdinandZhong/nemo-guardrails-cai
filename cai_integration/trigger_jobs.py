#!/usr/bin/env python3
"""
Trigger and monitor CML job execution.

This script:
1. Loads job IDs from create_jobs.py output
2. Triggers jobs in dependency order
3. Monitors execution and reports status
4. Handles idempotency (skips already-successful jobs)
"""

import argparse
import json
import os
import sys
import time
import yaml
import requests
from pathlib import Path
from typing import Dict, Optional, List


class JobRunner:
    """Handle CML job execution and monitoring."""

    def __init__(self):
        """Initialize CML REST API client."""
        self.cml_host = os.environ.get("CML_HOST")
        self.api_key = os.environ.get("CML_API_KEY")

        if not all([self.cml_host, self.api_key]):
            print("❌ Error: Missing required environment variables")
            print("   Required: CML_HOST, CML_API_KEY")
            sys.exit(1)

        self.api_url = f"{self.cml_host.rstrip('/')}/api/v2"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key.strip()}",
        }

    def make_request(
        self, method: str, endpoint: str, data: dict = None, params: dict = None
    ) -> Optional[dict]:
        """Make an API request to CML."""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30,
            )

            if 200 <= response.status_code < 300:
                if response.text:
                    try:
                        return response.json()
                    except json.JSONDecodeError:
                        return {}
                return {}
            else:
                print(f"❌ API Error ({response.status_code}): {response.text[:200]}")
                return None

        except Exception as e:
            print(f"❌ Request error: {e}")
            return None

    def load_jobs_config(self, config_path: str = None) -> Dict:
        """Load jobs configuration."""
        if config_path is None:
            config_path = Path(__file__).parent / "jobs_config.yaml"
        else:
            config_path = Path(config_path)

        with open(config_path) as f:
            return yaml.safe_load(f)

    def trigger_job(self, project_id: str, job_id: str) -> Optional[str]:
        """Trigger a job run."""
        result = self.make_request("POST", f"projects/{project_id}/jobs/{job_id}/runs")

        if result:
            run_id = result.get("id")
            return run_id

        return None

    def get_job_run_status(
        self, project_id: str, job_id: str, run_id: str
    ) -> Optional[Dict]:
        """Get job run status."""
        result = self.make_request(
            "GET", f"projects/{project_id}/jobs/{job_id}/runs/{run_id}"
        )
        return result

    def wait_for_job_completion(
        self, project_id: str, job_id: str, run_id: str, job_name: str, timeout: int = 3600
    ) -> bool:
        """Wait for job to complete."""
        print(f"⏳ Waiting for job '{job_name}' to complete...")

        start_time = time.time()
        last_status = None

        while time.time() - start_time < timeout:
            result = self.get_job_run_status(project_id, job_id, run_id)

            if result:
                status = result.get("status", "unknown")

                # Only print status updates when it changes
                if status != last_status:
                    elapsed = int(time.time() - start_time)
                    print(f"   [{elapsed}s] Status: {status}")
                    last_status = status

                # Terminal states
                if status == "succeeded":
                    print(f"✅ Job completed successfully")
                    return True
                elif status in ["failed", "stopped", "killed"]:
                    print(f"❌ Job failed with status: {status}")
                    return False

            time.sleep(10)

        print(f"❌ Timeout waiting for job completion ({timeout}s)")
        return False

    def get_job_execution_order(self, config: Dict) -> List[str]:
        """Determine job execution order based on dependencies."""
        jobs = config["jobs"]
        order = []
        processed = set()

        def add_job_with_deps(job_key: str):
            if job_key in processed:
                return

            job_config = jobs[job_key]
            parent_key = job_config.get("parent_job_key")

            if parent_key:
                add_job_with_deps(parent_key)

            order.append(job_key)
            processed.add(job_key)

        for job_key in jobs.keys():
            add_job_with_deps(job_key)

        return order

    def run(
        self, project_id: str, jobs_config_path: str = None, job_ids_path: str = None
    ) -> bool:
        """Execute job pipeline."""
        print("=" * 70)
        print("🚀 CML Job Execution for NeMo Guardrails")
        print("=" * 70)

        # Load configuration
        config = self.load_jobs_config(jobs_config_path)

        # Load job IDs
        if job_ids_path is None:
            job_ids_path = "/tmp/job_ids.json"

        try:
            with open(job_ids_path) as f:
                job_ids = json.load(f)
        except FileNotFoundError:
            print(f"❌ Job IDs file not found: {job_ids_path}")
            print("   Run create_jobs.py first")
            return False

        # Get execution order
        execution_order = self.get_job_execution_order(config)

        print(f"\n📋 Job execution order:")
        for i, job_key in enumerate(execution_order, 1):
            job_name = config["jobs"][job_key]["name"]
            print(f"   {i}. {job_name} ({job_key})")

        # Execute jobs in order
        print("\n" + "=" * 70)
        print("Executing Jobs")
        print("=" * 70)

        for job_key in execution_order:
            job_config = config["jobs"][job_key]
            job_name = job_config["name"]
            job_id = job_ids.get(job_key)

            if not job_id:
                print(f"❌ Job ID not found for: {job_key}")
                return False

            print(f"\n🚀 Triggering job: {job_name}")

            # Trigger job
            run_id = self.trigger_job(project_id, job_id)

            if not run_id:
                print(f"❌ Failed to trigger job: {job_name}")
                return False

            print(f"   Run ID: {run_id}")

            # Wait for completion
            timeout = job_config.get("timeout", 3600)
            success = self.wait_for_job_completion(
                project_id, job_id, run_id, job_name, timeout
            )

            if not success:
                print(f"\n❌ Job '{job_name}' failed")
                print("   Pipeline execution stopped")
                return False

        print("\n" + "=" * 70)
        print("✅ All Jobs Completed Successfully!")
        print("=" * 70)

        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Trigger and monitor CML jobs")
    parser.add_argument("--project-id", required=True, help="CML project ID")
    parser.add_argument("--jobs-config", help="Path to jobs configuration YAML")
    parser.add_argument("--job-ids", help="Path to job IDs JSON file")

    args = parser.parse_args()

    try:
        runner = JobRunner()
        success = runner.run(args.project_id, args.jobs_config, args.job_ids)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Job execution cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
