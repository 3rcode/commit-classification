import os
import re

ROOTDIR = os.path.abspath(os.path.dirname(__file__))

# HEADERS use for Github REST API
github_token = "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"
HEADERS = {
    "Authorization": f"token {github_token}",   
    "Accept": "application/vnd.github.v3+json"
}  
CM = r"https:\/\/github\.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/commit\/[a-zA-Z0-9]+"
PR = r"https:\/\/github\.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/pull\/[0-9]+"
IS = r"https:\/\/github\.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/issues\/[0-9]+"
bot_names = [
    "bot",
    "jenkins",
    "travis",
    "circleci",
    "github-actions",
    "dependabot",
    "codecov",
    "greenkeeper",
    "renovate",
    "commitlint",
    "husky",
    "probot",
    "octokit"
]
BOT = re.compile(fr'\b({"|".join(re.escape(name) for name in bot_names)})\b', re.IGNORECASE)
# VALID_RN_NUM and VALID_LINK_NUM use for assess if a repo can use to build dataset 
# A repo is assessed valid for this problem if it satisfy condition that at least VALID_RN_NUM 
# release note has at least VALID_LINK_NUM link to "change descriptor" (commit, issue, pull request)
VALID_RN_NUM = 5
VALID_LINK_NUM = 5