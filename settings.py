import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
github_token = "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"
HEADERS = {
    "Authorization": f"token {github_token}",   
    "Accept": "application/vnd.github.v3+json"
}