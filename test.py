import pandas as pd
import requests
from settings import HEADERS
import re
pd.set_option('display.max_rows', None)

def get_repo_topic():
  raw_repos = pd.read_csv("raw_repos.csv")
  no_topic_repos = []
  topics = {"repo": [], "topic": []}
  error = open("error_log.txt", mode="a+")
  for repo in raw_repos["Repo"]:
    print(repo)
    try:
      url = f"https://api.github.com/repos/{repo}"
      topics = requests.get(url, headers=HEADERS).json()["topics"]
      if not topics:
        no_topic_repos.append(repo)
      for i in range(len(topics)):
        topics["repo"].append(repo)
        topics["topic"].append(topics[i])
    except Exception as e:
      error.write(f"Encounter error while get info of {repo}: {e.message if hasattr(e, 'message') else ''}\n")

  no_topic_repos = pd.DataFrame({"Repo": no_topic_repos})
  no_topic_repos.to_csv("statistic/no_topic_repos.csv", index=False)
  topics = pd.DataFrame(topics)
  topics.to_csv("statistic/topics.csv", index=False)

def filter_topic():
  topics = pd.read_csv("statistic/topics.csv")
  origin_repos = set(topics["repo"].unique().tolist())
  filtered = topics.loc[topics["topic"].isin(["education", "algorithm", "algorithms", "awesome",
                                          "30dayofjavascript", "30daysofjavascript", "100dayofcode",
                                          "100joursdecode", "awesome-list", "best-practices",
                                          "book", "learning", "lists", "checklist", "leetcode", "list",
                                          "scikit-learn", "interview", "demo", "guidelines", 
                                          "definition", "string-boot-examples"])]
  filtered_repos = set(filtered["repo"].unique().tolist())
  print(len(filtered_repos))
  left_repos = origin_repos - filtered_repos
  left_repos = pd.DataFrame({"Repo": list(left_repos)})
  left_repos.to_csv("statistic/filtered.csv", index=False)


def filter_project_name():
  # pattern = re.compile(r'\bcourse\b')
  # repos = pd.read_csv("raw_repos.csv")
  
  # for repo in repos["Repo"]:
  #   project = repo.split('/')[1]
  #   if pattern.findall(project):
  #     print(repo)
  filtered_topic_repos = pd.read_csv("statistic/filtered.csv")["Repo"]
  print(len(filtered_topic_repos))
  no_topic_repos = pd.read_csv("statistic/no_topic_repos.csv")["Repo"]
  print(len(no_topic_repos))
  left_repos = pd.concat([filtered_topic_repos, no_topic_repos], axis=0)
  print(len(left_repos.loc[:].unique().tolist()))


filter_project_name()

