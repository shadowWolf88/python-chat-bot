Quickstart — Local Testing & Developer Notes

1. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

3. Set env vars for testing

```bash
export DEBUG=1
export PIN_SALT=test_salt
export ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

4. Run the app

```bash
.venv/bin/python api.py
# open http://localhost:5000
```

5. Run tests

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest -q
# optional browser tests
.venv/bin/pip install playwright pytest-playwright
.venv/bin/python -m playwright install chromium
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest tests/browser_smoke_test.py -q -p pytest_playwright
```

6. Troubleshooting
- If system pytest plugins interfere, use `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` as above.
- Ensure `ENCRYPTION_KEY` is set before FHIR export tests.

Document last updated: 2026-01-22
