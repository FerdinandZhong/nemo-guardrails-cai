# CAI API Migration: Removing caikit Dependency

## Overview

This document describes the migration from `caikit` library to direct Cloudera AI (CAI) REST API calls in the nemo-guardrails-cai project.

### Problem
- `caikit` library is not published to PyPI
- Cannot be used in production deployments or automated environments
- Creates hard dependency that breaks CI/CD pipelines

### Solution
Replace all `caikit` usage with direct CAI REST API calls using the standard `requests` library.

## Architecture

### REST API Pattern

All CAI integration scripts now follow this pattern:

```python
class CAIClient:
    def __init__(self, cml_host: str, api_key: str):
        self.api_url = f"{cml_host.rstrip('/')}/api/v2"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key.strip()}",
        }

    def make_request(self, method: str, endpoint: str, data: dict = None) -> Optional[dict]:
        """Make authenticated request to CAI REST API"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data,
            timeout=30,
        )
        return response.json() if response.ok else None
```

## Files Using CAI API

### 1. **setup_project.py** ✅
- **Purpose**: Create CML projects and wait for git clone
- **Pattern**: Direct REST API calls via `make_request()`
- **Endpoints**:
  - `GET /projects` - List projects
  - `POST /projects` - Create project
  - `GET /projects/{id}` - Get project status

### 2. **create_jobs.py** ✅
- **Purpose**: Create CML jobs from configuration
- **Pattern**: Direct REST API calls via `make_request()`
- **Endpoints**:
  - `GET /projects/{id}/jobs` - List jobs
  - `POST /projects/{id}/jobs` - Create job
  - Supports parent job dependencies

### 3. **trigger_jobs.py** ✅
- **Purpose**: Trigger and monitor job execution
- **Pattern**: Direct REST API calls via `make_request()`
- **Endpoints**:
  - `POST /projects/{id}/jobs/{jobId}/runs` - Trigger job
  - `GET /projects/{id}/jobs/{jobId}/runs/{runId}` - Get run status

### 4. **launch_guardrails.py** ✅
- **Purpose**: Create CAI Application for NeMo Guardrails server
- **Pattern**: Direct REST API calls via `make_request()`
- **Endpoints**:
  - `POST /projects/{id}/applications` - Create application
  - `GET /projects/{id}/applications/{id}` - Get application status
- **Changes from caikit version**:
  - Removed: `from caikit import CMLClient`
  - Added: `make_request()` method for REST API
  - Updated: `create_application()` to use HTTP POST
  - Updated: `wait_for_app_ready()` to use HTTP GET polling
  - Updated: `save_connection_info()` to work with dictionary responses

## API Endpoints Reference

### Base URL
```
{CML_HOST}/api/v2
```

### Authentication
```
Authorization: Bearer {API_KEY}
```

### Common Endpoints

#### Projects
```
GET    /projects                          # List projects
POST   /projects                          # Create project
GET    /projects/{projectId}              # Get project
```

#### Jobs
```
GET    /projects/{projectId}/jobs         # List jobs
POST   /projects/{projectId}/jobs         # Create job
GET    /projects/{projectId}/jobs/{jobId}/runs/{runId}  # Get run status
POST   /projects/{projectId}/jobs/{jobId}/runs          # Trigger job
```

#### Applications
```
GET    /projects/{projectId}/applications              # List applications
POST   /projects/{projectId}/applications              # Create application
GET    /projects/{projectId}/applications/{appId}      # Get application status
```

## Response Handling

All endpoints return JSON with status code 200-299 for success:

```python
if 200 <= response.status_code < 300:
    return response.json()
else:
    logger.error(f"API Error ({response.status_code}): {response.text}")
    return None
```

## Error Handling

Best practices:
1. Check if `make_request()` returns `None` (API error)
2. Validate required fields in response (e.g., `"id"`)
3. Use timeout for all requests (default: 30 seconds)
4. Log detailed error messages for debugging

```python
result = deployer.make_request("POST", "projects", data=project_data)
if not result:
    logger.error("Failed to create project")
    return False

project_id = result.get("id")
if not project_id:
    logger.error("No project ID in response")
    return False
```

## Migration Checklist

- [x] Remove caikit imports from launch_guardrails.py
- [x] Implement make_request() for REST API calls
- [x] Update all caikit usages to REST calls
- [x] Add proper error handling and validation
- [x] Verify setup_project.py uses REST API
- [x] Verify create_jobs.py uses REST API
- [x] Verify trigger_jobs.py uses REST API
- [ ] Test in CAI environment
- [ ] Update deployment documentation

## Testing

### Local Testing
```bash
# Verify imports work
python3 -c "import requests; import yaml; print('OK')"

# Check for caikit references
grep -r "caikit\|CMLClient" cai_integration/
# Should return only comments/documentation
```

### CAI Testing
1. Set required environment variables:
   ```bash
   export CML_HOST="https://your-cai-instance"
   export CML_API_KEY="your-api-key"
   export CDSW_PROJECT_ID="project-id"
   ```

2. Run deployment scripts:
   ```bash
   python3 cai_integration/setup_project.py
   python3 cai_integration/create_jobs.py --project-id <id>
   python3 cai_integration/trigger_jobs.py --project-id <id>
   python3 cai_integration/launch_guardrails.py
   ```

## Benefits

1. **No External Dependencies**: Only uses standard `requests` library
2. **Transparency**: Direct API calls are easier to debug and understand
3. **Flexibility**: Can easily extend with new API endpoints
4. **Maintainability**: Pattern is consistent across all integration scripts
5. **Robustness**: Better error handling and response validation

## References

- **ray-serve-cai**: Reference implementation for CAI integration patterns
- **CAI_AMP_Synthetic_Data_Studio**: Reference for build system patterns
- CAI REST API Documentation: Contact Cloudera support for API reference

## Future Improvements

1. Add retry logic with exponential backoff
2. Implement request caching for repeated queries
3. Add support for CAI workspace/runtime selection
4. Create shared CAIClient utility class
5. Add comprehensive logging and monitoring
