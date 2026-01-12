# Credentials Migration Guide

## ⚠️ Security Issue

This codebase currently has **hardcoded credentials** in multiple files. This is a **critical security vulnerability** that needs to be addressed.

## 🎯 What Changed

We've created a centralized credentials management system that uses environment variables instead of hardcoded values.

### Files with Hardcoded Credentials (TO BE UPDATED):

1. **captura_cameras/camera_downloader_complete.py**
   - Line ~10: `USERNAME = "bk@aiknow.ai"`
   - Line ~11: `PASSWORD = "nR}CMryIT,8/5!3i9"`

2. **captura_cameras_debug/corrigir_arquivos.py**
   - Line ~15: `LOGIN_EMAIL = "bk@aiknow.ai"`
   - Line ~16: `LOGIN_PASSWORD = "Sphbr7410"`

3. **sistema_recupera/script_alphaville.py**
   - Line ~20: `usuario = "adriana.cls"`
   - Line ~21: `senha = "2099cla"`

## 📋 Migration Steps

### Step 1: Install python-dotenv

```bash
pip install python-dotenv
```

Or add to your requirements.txt:
```
python-dotenv>=1.0.0
```

### Step 2: Create .env File

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your actual credentials
nano .env  # or use your preferred editor
```

**IMPORTANT:** Never commit `.env` to version control! It's already in `.gitignore`.

### Step 3: Update Your Scripts

#### Example: captura_cameras/camera_downloader_complete.py

**Before (INSECURE):**
```python
#!/usr/bin/env python3
import selenium

USERNAME = "bk@aiknow.ai"  # ❌ HARDCODED!
PASSWORD = "nR}CMryIT,8/5!3i9"  # ❌ HARDCODED!

def login():
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
```

**After (SECURE):**
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.credentials import get_aivisual_credentials

# Get credentials from environment variables
USERNAME, PASSWORD = get_aivisual_credentials()  # ✅ SECURE!

def login():
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
```

#### Example: captura_cameras_debug/corrigir_arquivos.py

**Before (INSECURE):**
```python
#!/usr/bin/env python3
import requests

LOGIN_EMAIL = "bk@aiknow.ai"  # ❌ HARDCODED!
LOGIN_PASSWORD = "Sphbr7410"  # ❌ HARDCODED!

def acessar_servidor():
    session.post(url, auth=(LOGIN_EMAIL, LOGIN_PASSWORD))
```

**After (SECURE):**
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.credentials import get_file_server_credentials

# Get credentials from environment variables
LOGIN_EMAIL, LOGIN_PASSWORD, SERVER_URL = get_file_server_credentials()  # ✅ SECURE!

def acessar_servidor():
    session.post(SERVER_URL, auth=(LOGIN_EMAIL, LOGIN_PASSWORD))
```

#### Example: sistema_recupera/script_alphaville.py

**Before (INSECURE):**
```python
#!/usr/bin/env python3
from selenium import webdriver

usuario = "adriana.cls"  # ❌ HARDCODED!
senha = "2099cla"  # ❌ HARDCODED!
url = "https://recupera.alphaville.com.br/Recupera/login/login.aspx"

def fazer_login():
    driver.find_element(By.ID, "username").send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(senha)
```

**After (SECURE):**
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add common module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.credentials import get_alphaville_credentials

# Get credentials from environment variables
usuario, senha, url = get_alphaville_credentials()  # ✅ SECURE!

def fazer_login():
    driver.find_element(By.ID, "username").send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(senha)
```

## 🔧 Validation Tool

Test your credentials setup:

```bash
python3 common/credentials.py
```

This will validate that all required environment variables are set correctly.

## 📝 Best Practices

### 1. Never Commit Credentials

```bash
# Add to .gitignore (already done)
.env
*.env
!.env.example
```

### 2. Use Different Credentials for Different Environments

```bash
# Development
cp .env.example .env.dev
# Edit .env.dev with dev credentials

# Production
cp .env.example .env.prod
# Edit .env.prod with prod credentials

# Load the right one
export ENV=dev
python3 -c "from dotenv import load_dotenv; load_dotenv('.env.$ENV')"
```

### 3. Rotate Credentials Regularly

If credentials were previously committed to git:
1. Change all passwords immediately
2. Use git-filter-branch or BFG Repo-Cleaner to remove from history
3. Force push to remote (if safe to do so)

### 4. Team Collaboration

Share `.env.example` with your team, but each developer maintains their own `.env` file:

```bash
# .env.example (commit this)
AIVISUAL_USER=your_email@example.com
AIVISUAL_PASS=your_password_here

# .env (NEVER commit this)
AIVISUAL_USER=real.email@company.com
AIVISUAL_PASS=actual_secure_password_123!
```

## 🧪 Testing with Environment Variables

Tests should use mock credentials:

```python
# conftest.py (already configured)
@pytest.fixture
def test_env_vars():
    test_vars = {
        'AIVISUAL_USER': 'test@example.com',
        'AIVISUAL_PASS': 'test_password_123',
    }
    for key, value in test_vars.items():
        os.environ[key] = value
    yield
    # Cleanup after test
```

## 🚀 Quick Start for New Developers

```bash
# 1. Clone repository
git clone <repo-url>
cd claude_skills

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Setup credentials
cp .env.example .env
nano .env  # Add your credentials

# 4. Validate
python3 common/credentials.py

# 5. Run tests
pytest tests/

# 6. Run scripts (credentials will be loaded automatically)
cd captura_cameras
python3 camera_downloader_complete.py
```

## ❓ Troubleshooting

### Error: "Environment variable 'AIVISUAL_USER' not found"

**Solution:**
```bash
# Make sure .env file exists
ls -la .env

# If not, create it
cp .env.example .env
nano .env

# Or export manually
export AIVISUAL_USER=your_email@example.com
export AIVISUAL_PASS=your_password
```

### Error: "ModuleNotFoundError: No module named 'dotenv'"

**Solution:**
```bash
pip install python-dotenv
```

### Error: "ModuleNotFoundError: No module named 'common'"

**Solution:**
```python
# Add this to the top of your script
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

## 📚 Additional Resources

- [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)
- [OWASP: Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [GitHub: Removing Sensitive Data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

## ✅ Migration Checklist

- [ ] Install python-dotenv
- [ ] Copy .env.example to .env
- [ ] Fill in actual credentials in .env
- [ ] Update captura_cameras/camera_downloader_complete.py
- [ ] Update captura_cameras_debug/corrigir_arquivos.py
- [ ] Update captura_cameras_debug/extrator_simples.py
- [ ] Update sistema_recupera/script_alphaville.py
- [ ] Remove hardcoded credentials from all files
- [ ] Test with validation tool: `python3 common/credentials.py`
- [ ] Run tests: `pytest tests/`
- [ ] Verify scripts still work
- [ ] Rotate any exposed passwords
- [ ] Clean git history if credentials were committed
- [ ] Update team documentation

---

**Status:** 🚧 IN PROGRESS - Scripts need to be updated to use new credentials system.
