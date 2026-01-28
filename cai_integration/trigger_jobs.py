#!/usr/bin/env python3
"""
Trigger and monitor CAI job execution.

This script:
1. Looks up jobs by name from jobs_config.yaml
2. Triggers only the root job (jobs with parent_job_key are auto-triggered by CAI)
3. Monitors root job execution and reports status
4. Child jobs with dependencies auto-trigger when parent succeeds

Pattern: Jobs with parent_job_key dependencies are automatically triggered
by CAI when the parent succeeds. We only need to trigger the root job.
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

    def list_jobs(self, project_id: str) -> Dict[str, str]:
        """List all jobs in a project and return name -> ID mapping."""
        result = self.make_request("GET", f"projects/{project_id}/jobs")

        if result:
            jobs = {}
            for job in result.get("jobs", []):
                job_name = job.get("name", "")
                job_id = job.get("id", "")
                if job_name and job_id:
                    jobs[job_name] = job_id
            return jobs
        return {}

    def get_job_id_by_name(self, project_id: str, job_name: str) -> Optional[str]:
        """Get job ID by job name."""
        jobs = self.list_jobs(project_id)
        return jobs.get(job_name)

    def trigger_job(self, project_id: str, job_id: str) -> Optional[str]:
        """Trigger a job run."""
        result = self.make_request("POST", f"projects/{project_id}/jobs/{job_id}/runs")

        if result:
            run_id = result.get("id")
            return run_id

        return None

    def get_job_run_status(self, project_id: str, job_id: str, run_id: str) -> Optional[Dict]:
        """Get job run status."""
        result = self.make_request("GET", f"projects/{project_id}/jobs/{job_id}/runs/{run_id}")
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

    def get_root_job(self, config: Dict) -> Optional[str]:
        """Find root job (job with no parent).

        Args:
            config: Jobs configuration dictionary

        Returns:
            Root job key, or None if not found
        """
        for job_key, job_config in config.get("jobs", {}).items():
            if job_config.get("parent_job_key") is None:
                return job_key
        return None

    def run(self, project_id: str, jobs_config_path: str = None) -> bool:
        """Execute job pipeline by triggering root job only.

        Note: Jobs with parent_job_key dependencies are automatically triggered
        by CAI when the parent succeeds. We only need to trigger the root job.

        Args:
            project_id: CAI project ID
            jobs_config_path: Path to jobs configuration YAML

        Returns:
            True if root job triggered successfully, False otherwise
        """
        print("=" * 70)
        print("🚀 NeMo Guardrails Job Execution")
        print("=" * 70)

        # Load configuration
        config = self.load_jobs_config(jobs_config_path)

        # Find root job (job with no parent)
        root_job_key = self.get_root_job(config)

        if not root_job_key:
            print(f"❌ Root job not found in configuration")
            return False

        root_job_config = config.get("jobs", {}).get(root_job_key, {})
        root_job_name = root_job_config.get("name", root_job_key)

        # Look up root job ID by name
        print(f"\n🔍 Looking up job: {root_job_name}")
        root_job_id = self.get_job_id_by_name(project_id, root_job_name)

        if not root_job_id:
            print(f"⚠️  Root job not found: {root_job_name}")
            print(f"   This is expected on initial deployment if script file doesn't exist yet")
            print(f"   Looking for first available job to trigger...")

            # Try to find first available job (usually setup_environment)
            all_jobs = self.list_jobs(project_id)
            if not all_jobs:
                print(f"❌ No jobs found in project")
                print("   Make sure jobs are created first (run create_jobs.py)")
                return False

            # Find first job that exists
            for job_key, job_config in config.get("jobs", {}).items():
                job_name = job_config.get("name", job_key)
                if job_name in all_jobs:
                    root_job_name = job_name
                    root_job_id = all_jobs[job_name]
                    root_job_config = job_config
                    print(f"   ✅ Using alternative root job: {root_job_name}")
                    break

            if not root_job_id:
                print(f"❌ No available jobs found")
                return False
        else:
            print(f"   ✅ Found job ID: {root_job_id}")

        # Display job dependency chain
        print(f"\n📋 Job dependency chain:")
        for job_key, job_config in config.get("jobs", {}).items():
            parent_key = job_config.get("parent_job_key")
            job_name = job_config.get("name", job_key)
            if parent_key:
                parent_name = config.get("jobs", {}).get(parent_key, {}).get("name", parent_key)
                print(f"   {parent_name} → {job_name}")
            else:
                print(f"   📍 {job_name} (root)")

        print(f"\n🔷 Triggering root job: {root_job_name}")
        print(f"   (Child jobs will auto-trigger via CAI dependencies)\n")

        # Trigger root job only
        run_id = self.trigger_job(project_id, root_job_id)

        if not run_id:
            print(f"   ❌ Failed to trigger root job\n")
            return False

        print(f"   ✅ Root job triggered: {run_id}\n")

        # Wait for root job completion
        timeout = root_job_config.get("timeout", 3600)
        if not self.wait_for_job_completion(
            project_id, root_job_id, run_id, root_job_name, timeout
        ):
            print(f"❌ Root job failed: {root_job_name}")
            return False

        print("=" * 70)
        print("✅ Root Job Completed Successfully!")
        print("=" * 70)
        print("\n💡 Note: Child jobs with dependencies will auto-trigger in CAI.")
        print("   Monitor them in the CAI UI: Jobs > Job Runs\n")

        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Trigger and monitor CML jobs")
    parser.add_argument("--project-id", required=True, help="CML project ID")
    parser.add_argument("--jobs-config", help="Path to jobs configuration YAML")

    args = parser.parse_args()

    try:
        runner = JobRunner()
        success = runner.run(args.project_id, args.jobs_config)
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
