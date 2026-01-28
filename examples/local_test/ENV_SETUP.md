# Environment Setup for Local Testing

This guide explains all environment variables needed for local testing.

## Quick Setup

### Option 1: Interactive Setup Script (Recommended)

```bash
# Run the setup script - it will guide you through everything
./examples/local_test/setup_env.sh
```

This will:
1. Create a `.env` file from template
2. Prompt you for your OpenAI API key
3. Check if dependencies are installed
4. Offer to install missing dependencies

### Option 2: Manual Setup

```bash
# 1. Copy the example file
cp examples/local_test/.env.example examples/local_test/.env

# 2. Edit the .env file and add your API key
nano examples/local_test/.env  # or use your preferred editor

# 3. Load the environment variables
export $(cat examples/local_test/.env | grep -v '^#' | xargs)
```

### Option 3: Direct Export (Quick Test)

```bash
# Just set the required variable directly
export OPENAI_API_KEY='sk-proj-your-key-here'
```

## Required Environment Variables

### OPENAI_API_KEY (Required)

**Purpose:** Authentication for OpenAI API

**Why needed:** The default rails (`self check input`, `self check output`) use OpenAI's API to check content for safety, jailbreaks, etc.

**How to get it:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-proj-` or `sk-`)
4. Keep it secret!

**Set it:**
```bash
export OPENAI_API_KEY='sk-proj-your-actual-key-here'
```

**Verify it's set:**
```bash
echo $OPENAI_API_KEY
# Should print: sk-proj-...
```

## Optional Environment Variables

### OPENAI_API_BASE

**Purpose:** Override the OpenAI API endpoint

**Default:** `https://api.openai.com/v1`

**When to use:**
- Using a proxy
- Using Azure OpenAI
- Using a custom OpenAI-compatible endpoint

**Example:**
```bash
# For Azure OpenAI
export OPENAI_API_BASE='https://your-resource.openai.azure.com'
```

### OPENAI_ORG_ID

**Purpose:** Specify organization for OpenAI API calls

**When to use:** You have multiple organizations in your OpenAI account

**Example:**
```bash
export OPENAI_ORG_ID='org-your-organization-id'
```

### SERVER_PORT

**Purpose:** Port for the guardrails server

**Default:** `8080`

**Example:**
```bash
export SERVER_PORT=9000
```

### LOG_LEVEL

**Purpose:** Control logging verbosity

**Default:** `INFO`

**Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`

**Example:**
```bash
export LOG_LEVEL=DEBUG  # See detailed logs
```

## Environment Variables NOT Needed for Local Testing

These are only needed for CAI deployment:

```bash
# CAI/CML - NOT needed locally
CML_HOST              # CAI instance URL
CML_API_KEY           # CAI API key
CDSW_APP_PORT         # Auto-set by CAI
CDSW_PROJECT_ID       # Auto-set by CAI

# GitHub - NOT needed locally
GITHUB_REPOSITORY     # For GitHub Actions
GH_PAT                # GitHub Personal Access Token
GITHUB_TOKEN          # Auto-set by GitHub Actions
```

## Complete Setup Checklist

- [ ] **OpenAI API Key obtained**
  - Go to https://platform.openai.com/api-keys
  - Create new key
  - Copy the key

- [ ] **Environment variable set**
  ```bash
  export OPENAI_API_KEY='sk-proj-...'
  ```

- [ ] **Verify it's set**
  ```bash
  echo $OPENAI_API_KEY  # Should print your key
  ```

- [ ] **NeMo Guardrails installed**
  ```bash
  pip install nemoguardrails
  ```

- [ ] **Test the setup**
  ```bash
  python examples/local_test/test_server.py
  ```

## Troubleshooting

### "OPENAI_API_KEY not set"

**Problem:** Environment variable is not loaded

**Solutions:**

1. **Check if it's set:**
   ```bash
   echo $OPENAI_API_KEY
   ```

2. **Re-export it:**
   ```bash
   export OPENAI_API_KEY='your-key-here'
   ```

3. **Check for spaces:**
   ```bash
   # WRONG - spaces around =
   export OPENAI_API_KEY = 'key'

   # CORRECT - no spaces
   export OPENAI_API_KEY='key'
   ```

4. **Make it permanent (optional):**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   echo "export OPENAI_API_KEY='your-key'" >> ~/.bashrc
   source ~/.bashrc
   ```

### "Invalid API key"

**Problem:** The key is incorrect or expired

**Solutions:**

1. **Check the key format:**
   - Should start with `sk-proj-` or `sk-`
   - No spaces or extra characters
   - Full key copied

2. **Generate a new key:**
   - Go to https://platform.openai.com/api-keys
   - Revoke old key
   - Create new key
   - Update environment variable

3. **Check API quota:**
   - Go to https://platform.openai.com/account/billing
   - Ensure you have credits

### "Environment variable not persisting"

**Problem:** Variable disappears after closing terminal

**Solution:** Add to shell profile

```bash
# For bash
echo "export OPENAI_API_KEY='your-key'" >> ~/.bashrc
source ~/.bashrc

# For zsh (macOS default)
echo "export OPENAI_API_KEY='your-key'" >> ~/.zshrc
source ~/.zshrc
```

### "Want to use different keys for different projects"

**Solution:** Use `.env` files per project

```bash
# In project directory
echo "OPENAI_API_KEY=project-specific-key" > .env

# Load when needed
export $(cat .env | grep -v '^#' | xargs)
```

## Security Best Practices

### DO ✅

- Keep API keys secret
- Use environment variables (not hardcoded)
- Rotate keys regularly
- Use `.gitignore` to exclude `.env` files
- Set spending limits on OpenAI account

### DON'T ❌

- Commit API keys to git
- Share API keys in chat/email
- Use production keys for testing
- Hardcode keys in source code

### Protecting Your Keys

```bash
# 1. Add .env to .gitignore (already done in this project)
echo ".env" >> .gitignore

# 2. Check what would be committed
git status

# 3. If you accidentally committed a key:
# - Revoke it immediately on OpenAI platform
# - Remove from git history (use BFG Repo-Cleaner)
# - Generate new key
```

## Testing Your Setup

### 1. Check Environment

```bash
# Run the check
python -c "
import os
key = os.environ.get('OPENAI_API_KEY')
if key:
    print(f'✅ API key is set: {key[:10]}...')
else:
    print('❌ API key is NOT set')
"
```

### 2. Test OpenAI Connection

```bash
# Quick API test
python -c "
from openai import OpenAI
import os
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
response = client.chat.completions.create(
    model='gpt-3.5-turbo',
    messages=[{'role': 'user', 'content': 'Hi'}],
    max_tokens=10
)
print('✅ OpenAI API is working!')
print(f'Response: {response.choices[0].message.content}')
"
```

### 3. Test Guardrails

```bash
# Run the full test
python examples/local_test/test_server.py
```

## Summary

**For local testing, you ONLY need:**

```bash
export OPENAI_API_KEY='sk-proj-your-key-here'
```

**That's it!** Everything else is optional or only needed for deployment.

## Quick Reference

```bash
# Setup (one time)
./examples/local_test/setup_env.sh

# Or manual
export OPENAI_API_KEY='sk-proj-...'

# Verify
echo $OPENAI_API_KEY

# Start server
python examples/local_test/test_server.py

# Test (in another terminal)
python examples/local_test/test_client.py
```

Done! 🚀
