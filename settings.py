import os

ROOTDIR = os.path.abspath(os.path.dirname(__file__))

# HEADERS use for Github REST API
github_token = "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"
HEADERS = {
    "Authorization": f"token {github_token}",   
    "Accept": "application/vnd.github.v3+json"
}  

# VALID_RN_NUM and VALID_LINK_NUM use for assess if a repo can use to build dataset 
# A repo is assessed valid for this problem if it satisfy condition that at least VALID_RN_NUM 
# release note has at least VALID_LINK_NUM link to "change descriptor" (commit, issue, pull request)
VALID_RN_NUM = 5
VALID_LINK_NUM = 5