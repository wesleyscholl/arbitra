# 🚨 Quick Fix for Import Error

You're seeing this error:
```
ModuleNotFoundError: No module named 'src'
```

## The Solution (30 seconds)

Run this in your terminal:

```bash
cd arbitra
source venv/bin/activate
pip install -e .
./run_tests.sh
```

That's it! Tests should now pass.

## What This Does

The `pip install -e .` command installs your package in **editable mode**, which creates links so Python can find your `src` directory. This is required for the tests to import from `src.risk`.

## Automated Fix

Or just run the install script which does everything:

```bash
./install.sh
```

## Verify It Worked

```bash
# This should print "✓ Package importable"
python -c "import src.risk; print('✓ Package importable')"

# Then run tests
./run_tests.sh
```

## Still Having Issues?

See **TROUBLESHOOTING.md** for comprehensive solutions.

---

**Why is this needed?** Python packages need to be installed (even local ones) for imports to work. The `-e` flag makes it "editable" so changes to your code are immediately available without reinstalling.
