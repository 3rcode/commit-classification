import os
from settings import ROOTDIR
import pandas as pd
import numpy as np
import re


repo_path = os.path.join(ROOTDIR, "valid_repos.csv")
repos = pd.read_csv(repo_path)
num_rn = []
num_pr = []
num_issue = []
num_commit = []
oldest = latest = []
bot_pattern = re.compile(r"/(?:bot|jenkins|travis|circleci|github-actions|dependabot|codecov|greenkeeper|renovate|commitlint|husky|probot|octokit)\b/i")
for repo in repos["Repo"]:
    print(repo)
    folder = os.path.join(ROOTDIR, "data", repo.replace('/', '_'))
    rn = pd.read_csv(os.path.join(folder, "rn_info_sorted.csv"))
    rn["published_at"] = pd.to_datetime(rn["published_at"])
    # pr = pd.read_csv(os.path.join(folder, "pr_info.csv"))
    # issue = pd.read_csv(os.path.join(folder, "issue_info.csv"))
    # commit = pd.read_csv(os.path.join(folder, "commit_sorted.csv"))
    num_rn.append(len(rn))
    oldest.append(rn["published_at"].iloc[-1])
    latest.append(rn["published_at"].iloc[0])
    # num_pr.append(len(pr))
    # num_issue.append(len(issue))
    # num_commit.append(len(commit))

oldest = [x.to_pydatetime() for x in oldest]
latest = [x.to_pydatetime() for x in latest]

num_rn = np.array(num_rn)
print("Total num release note:", np.sum(num_rn))
print("Mean num release note:", np.mean(num_rn))
print("Max num release note:", np.max(num_rn))
print("Min num release note:", np.min(num_rn))
print("Median num release note:", np.median(num_rn))
print("Oldest release note:", min(oldest))
print("Latest release note:", max(latest))
# data_info = pd.DataFrame({"repo": repos["Repo"], "# rn": num_rn, "# commit": num_commit, 
#                           "# pr": num_pr, "# issue": num_issue})
# print(data_info)

# print("Toal release note:", sum(data_info["# rn"]))
# print("Total commit:", sum(data_info["# commit"]))
# print("Total pull request:", sum(data_info["# pr"]))
# print("Total issue:", sum(data_info["# issue"]))