# Contributing to Gmail Guardian

Thank you for your interest in improving Gmail Guardian. We welcome bug fixes, documentation updates, and new unit tests.

---

## Development Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Glenskii/Glenski-Toolkit.git
   cd Glenski-Toolkit/skills/inbox-guardian-for-gmail
   ```

2. **Create a Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\Activate.ps1
   ```

3. **Install Requirements:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

---

## Running Tests

We maintain complete unit test coverage for classification logic, input sanitization, and API error handling:

```bash
pytest tests/ -v
```

---

## Guidelines for Pull Requests

1. **Safety First**: Do not add irreversible deletion. Quarantine and review must remain the standard flow.
2. **Input Validation**: Never pass unvalidated text directly into search queries.
3. **Clear Writing**: Avoid excessive jargon or marketing claims. Do not use em dashes in documentation. Use straightforward, readable English.
4. **Test Coverage**: Include unit tests for any new filter rules or code changes.
