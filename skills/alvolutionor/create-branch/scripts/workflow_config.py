import json
import os
from pathlib import Path
from urllib.parse import urlparse


def load_settings():
    path = os.environ.get("WORKFLOW_CONFIG")
    if not path:
        raise ValueError("Set WORKFLOW_CONFIG to a private JSON configuration file outside the repository")
    config = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(config, dict):
        raise ValueError("Workflow configuration must be a JSON object")
    return config


def required(config, key):
    value = config.get(key)
    if value is None or value == "":
        raise ValueError(f"Missing workflow configuration: {key}")
    return value


def jira_url(config):
    value = str(required(config, "jira_url")).rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path:
        raise ValueError("jira_url must be an HTTPS origin without credentials, query, fragment or path")
    return value


def jira_session(config):
    import requests
    session = requests.Session()
    session.auth = (os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"])
    session.headers["Accept"] = "application/json"
    return session


def bitbucket_session():
    import requests
    session = requests.Session()
    session.auth = (os.environ["BITBUCKET_USERNAME"], os.environ["BITBUCKET_API_TOKEN"])
    session.headers["Accept"] = "application/json"
    return session
