from urllib.parse import urlparse

import requests

import workflow_config


class WorkflowError(Exception):
    pass


def settings():
    config = workflow_config.load_settings()
    for key in ("base_branch", "reviewers", "review_bot_user_id", "review_channel_id", "announcement_channel_id"):
        workflow_config.required(config, key)
    if not isinstance(config["reviewers"], list) or not config["reviewers"] or any(not item.get("uuid") for item in config["reviewers"]):
        raise WorkflowError("Configure at least one reviewer UUID")
    return config


def bitbucket_session():
    return workflow_config.bitbucket_session()


class Bitbucket:
    def __init__(self, session=None):
        self.session = session if session is not None else bitbucket_session()

    def request(self, method, path, **kwargs):
        url = path if path.startswith("https://") else "https://api.bitbucket.org/2.0/" + path
        if urlparse(url).hostname != "api.bitbucket.org":
            raise WorkflowError("Unexpected Bitbucket API host")
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
        except requests.RequestException as error:
            raise WorkflowError("Bitbucket request outcome unavailable; inspect before retrying a write") from error
        if response.status_code >= 400:
            raise WorkflowError(f"Bitbucket HTTP {response.status_code}; PR creation requires pull-request write permission")
        return response.json()

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def pages(self, path, params=None):
        while path:
            result = self.get(path, params=params)
            yield from result.get("values", [])
            path = result.get("next")
            params = None
