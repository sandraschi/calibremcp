# 📦 PyPI Publishing Guide - Complete Walkthrough

**Complete guide to publishing notepadpp-mcp on the Python Package Index (PyPI)**

**Date**: October 8, 2025
**Status**: Ready to publish
**Target**: Make `pip install notepadpp-mcp` work globally

---

## 🎯 **What is PyPI?**

**PyPI** = **Python Package Index** (https://pypi.org)

**What it does**:
- Central repository for Python packages
- Allows anyone to install your package via `pip install your-package`
- Public, searchable, versioned
- **100,000+** packages available

**Why publish to PyPI**:
- ✅ Easy installation: `pip install notepadpp-mcp`
- ✅ Automatic dependency resolution
- ✅ Version management
- ✅ Discoverability (searchable on PyPI)
- ✅ Professional credibility
- ✅ Integration with tools (pip, poetry, etc.)

---

## 📊 **PyPI vs Test PyPI**

| Feature | **Test PyPI** | **Production PyPI** |
|---------|---------------|-------------------|
| **URL** | https://test.pypi.org | https://pypi.org |
| **Purpose** | Testing uploads | Real production |
| **Command** | `--repository testpypi` | Default |
| **Separate account** | ✅ Yes | ✅ Yes |
| **Practice first** | ✅ Always use first | ✅ After testing |

**Best practice**: Upload to Test PyPI first, verify, then upload to real PyPI!

---

## 🔑 **Step 1: Create PyPI Account**

### **A. Register on PyPI**

**Production PyPI**:
1. Go to: https://pypi.org/account/register/
2. Fill in:
   - Username (e.g., `sandraschi`)
   - Email address
   - Password (strong!)
   - Full name
3. ✅ Verify email (check inbox)
4. ✅ Account created!

**Test PyPI** (separate account):
1. Go to: https://test.pypi.org/account/register/
2. Same process as above
3. **Different account** from production!

---

### **B. Enable Two-Factor Authentication (2FA)**

**REQUIRED for uploading packages!**

1. Log in to PyPI
2. Go to: https://pypi.org/manage/account/
3. Click "Add 2FA with authentication application"
4. Options:
   - **Authenticator app** (Google Authenticator, Authy, etc.)
   - **Security key** (YubiKey, etc.)
5. Scan QR code with your app
6. Enter verification code
7. ✅ Save recovery codes somewhere safe!

**Recovery codes**: Store these securely! If you lose your phone, you'll need them.

---

## 🔐 **Step 2: Create API Token**

**API tokens** = Secure way to upload packages (better than password)

### **A. Generate Token on PyPI**

1. Log in to https://pypi.org
2. Go to: https://pypi.org/manage/account/token/
3. Click **"Add API token"**
4. Fill in:
   - **Token name**: `notepadpp-mcp-upload` (descriptive name)
   - **Scope**:
     - **Option 1**: "Entire account" (can upload any package)
     - **Option 2**: "Project" → Select `notepadpp-mcp` (package-specific, more secure)
5. Click **"Add token"**
6. ✅ **COPY THE TOKEN IMMEDIATELY!** (shown only once)

**Token format**:
```
pypi-AgEIcHlwaS5vcmcCJGFiY2RlZi0xMjM0LTU2NzgtOTBhYi1jZGVmMTIzNDU2NzgAAABB...
```

**⚠️ CRITICAL**: Save this token immediately! You can't see it again!

---

### **B. Store Token Securely**

**Option 1: In `.pypirc` file** (Recommended)

Create or edit `~/.pypirc` (Windows: `C:\Users\YourName\.pypirc`):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJGFiY... (your actual token)

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJGFiY... (your test.pypi token)
```

**Security**:
```powershell
# Set file permissions (Windows PowerShell)
$acl = Get-Acl "$env:USERPROFILE\.pypirc"
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME, "FullControl", "Allow"
)
$acl.SetAccessRule($rule)
Set-Acl "$env:USERPROFILE\.pypirc" $acl
```

---

**Option 2: Environment Variable**

```powershell
# Set in PowerShell (temporary)
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-AgEIcHlwaS5vcmcCJGFiY..."

# Or add to PowerShell profile (permanent)
# Edit: $PROFILE
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-AgEIcHlwaS5vcmcCJGFiY..."
```

---

**Option 3: Pass directly to twine** (least secure)

```bash
twine upload dist/* -u __token__ -p pypi-AgEIcHlwaS5vcmcCJGFiY...
```

---

## 📦 **Step 3: Prepare Your Package**

### **A. Verify Package Structure**

```
notepadpp-mcp/
├── src/
│   └── notepadpp_mcp/
│       ├── __init__.py
│       └── tools/
│           └── server.py
├── pyproject.toml         ← Package metadata
├── README.md              ← PyPI description
├── LICENSE                ← Required!
├── MANIFEST.in            ← Include extra files
└── requirements.txt       ← Dependencies
```

**Check `pyproject.toml`**:

```toml
[project]
name = "notepadpp-mcp"
version = "1.2.0"  # Update for each release!
description = "MCP Server for Notepad++ automation"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Sandra Schi", email = "your@email.com"}
]
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=2.12.0",
    "mcp>=1.0.0,<2.0.0",
    "anyio>=4.0.0,<5.0.0",
    "psutil>=5.9.0",
    "pywin32==311; platform_system=='Windows'",
    "requests>=2.31.0",
]
keywords = ["notepad++", "mcp", "automation", "windows"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[project.urls]
Homepage = "https://github.com/sandraschi/notepadpp-mcp"
Repository = "https://github.com/sandraschi/notepadpp-mcp"
Documentation = "https://github.com/sandraschi/notepadpp-mcp/blob/main/README.md"
"Bug Tracker" = "https://github.com/sandraschi/notepadpp-mcp/issues"

[project.scripts]
notepadpp-mcp = "notepadpp_mcp.tools.server:main"
```

---

### **B. Update Version Number**

**Before EVERY upload to PyPI**:

1. Edit `pyproject.toml`:
   ```toml
   version = "1.2.0"  # Increment this!
   ```

2. Follow **Semantic Versioning** (SemVer):
   - **Major** (1.x.x): Breaking changes
   - **Minor** (x.2.x): New features, backward compatible
   - **Patch** (x.x.0): Bug fixes only

**Examples**:
- `1.2.0` → `1.2.1` (bug fix)
- `1.2.0` → `1.3.0` (new feature)
- `1.2.0` → `2.0.0` (breaking change)

**⚠️ Can't re-upload same version!** Each upload must have new version number.

---

### **C. Create LICENSE File**

**Required by PyPI!**

Create `LICENSE` file:

```text
MIT License

Copyright (c) 2025 Sandra Schi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🛠️ **Step 4: Build the Package**

### **A. Install Build Tools**

```powershell
# Install build tools
pip install --upgrade build twine

# Verify
python -m build --version
twine --version
```

---

### **B. Clean Previous Builds**

```powershell
# Remove old build artifacts
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
```

---

### **C. Build Distribution Files**

```powershell
# Build both wheel and source distribution
python -m build

# Output:
# dist/
#   notepadpp_mcp-1.2.0-py3-none-any.whl    ← Wheel (binary)
#   notepadpp-mcp-1.2.0.tar.gz              ← Source distribution
```

**What gets created**:
- **`.whl`** file: Wheel (fast to install)
- **`.tar.gz`** file: Source distribution (fallback)

---

### **D. Verify Build**

```powershell
# Check contents of wheel
python -m zipfile -l dist/notepadpp_mcp-1.2.0-py3-none-any.whl

# Check package metadata
twine check dist/*

# Should show:
# Checking dist/notepadpp-mcp-1.2.0.tar.gz: PASSED
# Checking dist/notepadpp_mcp-1.2.0-py3-none-any.whl: PASSED
```

---

## 🚀 **Step 5: Upload to PyPI**

### **A. Upload to Test PyPI First** (ALWAYS!)

```powershell
# Upload to test.pypi.org
twine upload --repository testpypi dist/*

# Or with explicit URL:
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Enter credentials if not in .pypirc:
# Username: __token__
# Password: pypi-AgEIcHlwaS5vcmcCJGFiY... (your token)
```

**Output**:
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading notepadpp_mcp-1.2.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 52.3/52.3 kB • 00:01
Uploading notepadpp-mcp-1.2.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 48.5/48.5 kB • 00:01

View at:
https://test.pypi.org/project/notepadpp-mcp/1.2.0/
```

---

### **B. Test Install from Test PyPI**

```powershell
# Create test environment
python -m venv test-env
.\test-env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ notepadpp-mcp

# Test it works
notepadpp-mcp --version
python -m notepadpp_mcp.tools.server

# If works: ✅ Ready for production!
# If broken: ❌ Fix and re-upload with new version
```

**Why `--extra-index-url`?**
- Test PyPI doesn't have all dependencies
- Falls back to real PyPI for dependencies (fastmcp, etc.)

---

### **C. Upload to Production PyPI**

**Only after testing on Test PyPI!**

```powershell
# Upload to real PyPI
twine upload dist/*

# Output:
Uploading distributions to https://upload.pypi.org/legacy/
Uploading notepadpp_mcp-1.2.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 52.3/52.3 kB • 00:02
Uploading notepadpp-mcp-1.2.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 48.5/48.5 kB • 00:02

View at:
https://pypi.org/project/notepadpp-mcp/1.2.0/
```

**🎉 DONE! Your package is live!**

---

### **D. Verify Production Install**

```powershell
# In fresh environment
pip install notepadpp-mcp

# Test
notepadpp-mcp --version

# Should work globally now!
```

---

## 📝 **Step 6: Post-Publication**

### **A. Add PyPI Badge to README**

```markdown
[![PyPI version](https://img.shields.io/pypi/v/notepadpp-mcp.svg)](https://pypi.org/project/notepadpp-mcp/)
[![Python versions](https://img.shields.io/pypi/pyversions/notepadpp-mcp.svg)](https://pypi.org/project/notepadpp-mcp/)
[![Downloads](https://pepy.tech/badge/notepadpp-mcp)](https://pepy.tech/project/notepadpp-mcp)
```

---

### **B. Update Documentation**

**README.md**:
```markdown
## Installation

```bash
pip install notepadpp-mcp
```

**From source**:
```bash
git clone https://github.com/sandraschi/notepadpp-mcp.git
cd notepadpp-mcp
pip install -e .
```
```

---

### **C. Create GitHub Release**

1. Go to: https://github.com/sandraschi/notepadpp-mcp/releases
2. Click "Create a new release"
3. Tag: `v1.2.0`
4. Title: `v1.2.0 - Plugin Ecosystem & MCPB Packaging`
5. Description: Copy from CHANGELOG.md
6. Attach: `dist/notepadpp-mcp-1.2.0.tar.gz`
7. ✅ Publish release

---

## 🔄 **Step 7: Updating Package**

**For each new version**:

1. **Update code/docs**
2. **Increment version** in `pyproject.toml`
3. **Update CHANGELOG.md**
4. **Commit changes**:
   ```bash
   git commit -am "Release v1.2.1"
   git tag v1.2.1
   git push origin main --tags
   ```
5. **Build**:
   ```powershell
   Remove-Item -Recurse dist -ErrorAction SilentlyContinue
   python -m build
   ```
6. **Test on Test PyPI**:
   ```powershell
   twine upload --repository testpypi dist/*
   ```
7. **Upload to Production**:
   ```powershell
   twine upload dist/*
   ```
8. **Create GitHub Release**

---

## ⚠️ **Common Errors & Solutions**

### **Error 1: "File already exists"**

```
ERROR: HTTPError: 400 Bad Request
File already exists. See https://pypi.org/help/#file-name-reuse
```

**Cause**: Trying to upload same version again
**Solution**: Increment version number in `pyproject.toml`

---

### **Error 2: "Invalid authentication credentials"**

```
ERROR: HTTPError: 403 Forbidden
Invalid or non-existent authentication information
```

**Cause**: Wrong token or username
**Solution**:
- Username must be `__token__` (with underscores!)
- Password is your API token starting with `pypi-AgEI...`

---

### **Error 3: "Package name already taken"**

```
ERROR: The name 'notepadpp-mcp' is already claimed
```

**Cause**: Someone else registered this name
**Solution**:
- Choose different name (e.g., `notepadpp-mcp-server`)
- Contact PyPI admins if you own the name

---

### **Error 4: "README rendering failed"**

```
WARNING: `long_description_content_type` missing
```

**Solution**: Add to `pyproject.toml`:
```toml
[project]
readme = {file = "README.md", content-type = "text/markdown"}
```

---

### **Error 5: "Missing required metadata"**

```
ERROR: `description` is a required field
```

**Solution**: Ensure `pyproject.toml` has all required fields:
- `name`
- `version`
- `description`
- `authors`

---

## 📊 **PyPI Package Page**

**After publishing**, your package page shows:

**URL**: https://pypi.org/project/notepadpp-mcp/

**Displays**:
- ✅ Package name & version
- ✅ README (rendered from your README.md)
- ✅ Installation command: `pip install notepadpp-mcp`
- ✅ Dependencies
- ✅ Python version requirements
- ✅ Download statistics
- ✅ Project links (GitHub, docs, etc.)
- ✅ Version history
- ✅ Classifiers (tags/categories)

---

## 🎯 **Best Practices**

### **1. Version Management**

```toml
# NEVER reuse version numbers!
# PyPI is immutable - can't delete/replace versions

# Good versioning:
1.0.0 → 1.0.1 → 1.1.0 → 1.2.0 → 2.0.0

# Bad:
1.0.0 → 1.0.0 (rejected!)
```

---

### **2. Testing**

```powershell
# ALWAYS test before production upload!

# 1. Test locally
pip install -e .
# Run tests

# 2. Test on Test PyPI
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ notepadpp-mcp
# Verify works

# 3. THEN upload to production
twine upload dist/*
```

---

### **3. Security**

```powershell
# NEVER commit tokens to git!
# Add to .gitignore:
echo ".pypirc" >> .gitignore
echo "*.token" >> .gitignore

# Use package-scoped tokens (not account-wide)
# Rotate tokens periodically
# Store recovery codes securely
```

---

### **4. Documentation**

```markdown
# Good README for PyPI:
- Clear installation instructions
- Usage examples
- Requirements
- License
- Links to full docs
- Screenshots (if GUI)
- Badges (PyPI version, downloads, etc.)
```

---

## 🚀 **Automation with GitHub Actions**

**Optional**: Auto-publish on git tag

Create `.github/workflows/publish-pypi.yml`:

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

**Setup**:
1. Add PyPI token to GitHub Secrets:
   - Settings → Secrets → Actions
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI token

2. Create git tag and push:
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```

3. GitHub Actions auto-publishes!

---

## 📚 **Resources**

**Official Docs**:
- PyPI: https://pypi.org
- Test PyPI: https://test.pypi.org
- Packaging Guide: https://packaging.python.org
- Twine: https://twine.readthedocs.io

**Tools**:
- `build`: https://pypa-build.readthedocs.io
- `twine`: https://twine.readthedocs.io
- `setuptools`: https://setuptools.pypa.io

**Security**:
- 2FA Setup: https://pypi.org/help/#twofa
- API Tokens: https://pypi.org/help/#apitoken

---

## ✅ **Quick Checklist**

**Before first upload**:
- [ ] Create PyPI account
- [ ] Enable 2FA
- [ ] Create API token
- [ ] Store token in `.pypirc`
- [ ] Create LICENSE file
- [ ] Update `pyproject.toml` metadata
- [ ] Write good README.md

**For each release**:
- [ ] Increment version number
- [ ] Update CHANGELOG.md
- [ ] Clean old builds: `Remove-Item dist -Recurse`
- [ ] Build: `python -m build`
- [ ] Check: `twine check dist/*`
- [ ] Test upload: `twine upload --repository testpypi dist/*`
- [ ] Test install from Test PyPI
- [ ] Production upload: `twine upload dist/*`
- [ ] Verify: `pip install notepadpp-mcp`
- [ ] Create GitHub release
- [ ] Update README badges

---

## 🎉 **Success!**

**After publishing**:

```bash
# Anyone in the world can now install:
pip install notepadpp-mcp

# Your package is discoverable on:
https://pypi.org/project/notepadpp-mcp/

# Download statistics available at:
https://pepy.tech/project/notepadpp-mcp
```

**Congratulations! You're now a published Python package author!** 🎊

---

*PyPI Publishing Guide*
*Created: October 8, 2025*
*For: notepadpp-mcp v1.2.0*
*Status: Ready to publish*

**Happy publishing!** 🚀📦
