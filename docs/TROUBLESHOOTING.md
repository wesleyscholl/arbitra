# Troubleshooting Guide

## Common Issues and Solutions

### 1. "ModuleNotFoundError: No module named 'src'"

**Problem**: Tests can't find the `src` package.

**Solution**: Install the package in editable mode:

```bash
# Make sure you're in the arbitra directory and venv is activated
source venv/bin/activate  # If not already activated
pip install -e .
```

**Why**: The `-e` flag installs the package in "editable" mode, creating links so Python can find your `src` directory.

**Quick fix**: Run `./install.sh` which handles everything.

---

### 2. "zsh: command not found: pip"

**Problem**: Virtual environment not activated.

**Solution**: Activate the virtual environment:

```bash
cd arbitra
source venv/bin/activate

# You should see (venv) in your prompt
```

**For Windows**:
```cmd
venv\Scripts\activate
```

---

### 3. Virtual Environment Doesn't Exist

**Problem**: No `venv` directory.

**Solution**: Create it:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -e .
```

**Or use the automated script**:
```bash
./install.sh
```

---

### 4. Tests Collect But Show 0% Coverage

**Problem**: Package installed but not in editable mode.

**Solution**: Reinstall in editable mode:

```bash
pip uninstall arbitra  # Remove if installed normally
pip install -e .       # Install in editable mode
```

---

### 5. "FAIL Required test coverage of 90% not reached"

**Problem**: Tests didn't run, so coverage is 0%.

**Root cause**: Usually due to import errors (see #1 above).

**Solution**: Fix import errors first, then coverage will be calculated correctly.

---

### 6. Permission Denied on Scripts

**Problem**: `./run_tests.sh` or `./install.sh` won't run.

**Solution**: Make them executable:

```bash
chmod +x run_tests.sh
chmod +x install.sh
chmod +x setup.sh
```

---

### 7. pytest-xprocess Warning

**Problem**: Warning about terminating processes.

**Solution**: This is just a reminder. If you see it, run:

```bash
pytest --xkill
```

But normally you can ignore it.

---

### 8. Import Errors with Hypothesis

**Problem**: `hypothesis` module not found.

**Solution**: Reinstall requirements:

```bash
pip install -r requirements.txt
```

---

### 9. Wrong Python Version

**Problem**: Python 3.10 or earlier.

**Solution**: Upgrade to Python 3.11+:

```bash
# macOS (Homebrew)
brew install python@3.11

# Check version
python3 --version

# Recreate venv with correct version
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

---

### 10. Podman Issues

#### "podman machine not running"
```bash
podman machine start
```

#### "Cannot connect to Podman"
```bash
# Check status
podman machine list

# Restart if needed
podman machine stop
podman machine start
```

#### "Port already in use"

Edit `podman-compose.yml` and change ports:
```yaml
ports:
  - "5433:5432"  # Instead of "5432:5432"
```

---

### 11. PostgreSQL Connection Refused

#### If using Podman:
```bash
# Check if running
podman-compose ps

# Restart services
podman-compose down
podman-compose up -d
```

#### If using local PostgreSQL:
```bash
# macOS
brew services list | grep postgres
brew services restart postgresql@15

# Linux
sudo systemctl status postgresql
sudo systemctl restart postgresql
```

---

### 12. Redis Connection Issues

```bash
# Check if running (Podman)
podman-compose ps

# Check if running (local - macOS)
brew services list | grep redis
brew services restart redis

# Test connection
redis-cli ping
# Should return: PONG
```

---

## Verification Steps

After fixing issues, verify everything works:

### 1. Check Virtual Environment
```bash
# Should show path to arbitra/venv
which python

# Should be 3.11 or higher
python --version
```

### 2. Check Package Installation
```bash
# Should succeed without error
python -c "import src.risk; print('✓ Package importable')"
```

### 3. Run Simple Test
```bash
# Should pass
pytest tests/risk/test_position_sizing.py::TestKellyCriterion::test_kelly_with_positive_edge -v
```

### 4. Full Test Suite
```bash
# Should pass all tests
./run_tests.sh
```

---

## Still Having Issues?

### Get Debug Info
```bash
# Show environment details
python --version
which python
pip list | grep -E "pytest|hypothesis"
ls -la | grep venv
pwd
```

### Clean Slate Approach
If all else fails, start fresh:

```bash
# 1. Delete everything
cd arbitra
deactivate  # If venv is active
rm -rf venv
rm -rf .pytest_cache
rm -rf __pycache__
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# 2. Fresh install
./install.sh

# 3. Test
./run_tests.sh
```

---

## Quick Reference Commands

```bash
# Install everything
./install.sh

# Activate venv (if not active)
source venv/bin/activate

# Install in editable mode
pip install -e .

# Run tests
./run_tests.sh
pytest tests/risk/ -v
make test-risk

# Check what's installed
pip list

# Verify imports work
python -c "import src.risk"

# Clean up
make clean
```

---

## Need More Help?

1. Check if issue is in the QUICKSTART.md guide
2. Review INSTALLATION.md for setup options
3. Look at test files for usage examples
4. Check project structure is correct:
   ```
   arbitra/
   ├── src/
   │   └── risk/
   │       ├── __init__.py
   │       ├── position_sizing.py
   │       └── circuit_breaker.py
   └── tests/
       └── risk/
           ├── test_position_sizing.py
           └── test_circuit_breaker.py
   ```
