import pandas as pd
import requests
from settings import HEADERS
import re
from markdown import markdown
from bs4 import BeautifulSoup
from make_data import github_api
pd.set_option('display.max_rows', None)

def get_repo_topic():
  raw_repos = pd.read_csv("raw_repos.csv")
  no_topic_repos = []
  df = {"Repo": [], "Topic": []}
  error = open("error_log.txt", mode="a+")
  for repo in raw_repos["Repo"]:
    print(repo)
    try:
      url = f"https://api.github.com/repos/{repo}"
      topics = requests.get(url, headers=HEADERS).json()["topics"]
      if not topics:
        no_topic_repos.append(repo)
      for topic in topics:
        df["Repo"].append(repo)
        df["Topic"].append(topic)
    except Exception as e:
      error.write(f"Encounter error while get info of {repo}: {e}\n")

  no_topic_repos = pd.DataFrame({"Repo": no_topic_repos})
  no_topic_repos.to_csv("statistic/no_topic_repos.csv", index=False)
  df = pd.DataFrame(df)
  df.to_csv("statistic/topics.csv", index=False)


def filter_topic():
  topics = pd.read_csv("statistic/topics.csv")
  origin_repos = set(topics["Repo"].unique().tolist())
  filtered = topics.loc[topics["Topic"].isin(["education", "algorithm", "algorithms", "awesome",
                                          "30dayofjavascript", "30daysofjavascript", "100dayofcode",
                                          "100joursdecode", "awesome-list", "best-practices",
                                          "book", "books", "learning", "lists", "checklist", "leetcode", 
                                          "list", "scikit-learn", "interview", "demo", "guidelines",
                                          "definition", "string-boot-examples", "docs", "udacity", 
                                          "hacktoberfest", "markdown", "developer-portfolio", "badges-markdown",
                                          "survey", "cheatsheet", "blog", "portfolio", "documentation", 
                                          "examples", "china", "guide", "curated-list", "tutorials"
                                          "ebook", "study-guide", "learn-to-code", "workshopper", "tips",
                                          "tip-and-tricks", "educational", "collection", "writing",
                                          "today-i-learned", "learn-in-public", "chinese-programmers",
                                          "course", "classroom", "30-days-of-python"])]
  filtered_repos = set(filtered["Repo"].unique().tolist())
  left_repos = origin_repos - filtered_repos
  filtered_repos = pd.DataFrame({"Repo": list(filtered_repos)})
  filtered_repos.to_csv("statistic/filtered_topic.csv", index=False)
  left_repos = pd.DataFrame({"Repo": list(left_repos)})
  left_repos.to_csv("statistic/left_repos_topic.csv", index=False)


def filter_project_name():
  pattern = re.compile(r'^.*(\bcourse\b)|(book)|(interview)|(example)|(dataset)|(datasets)|(roadmap)|(cheat-sheet)|(cheatsheet)|(cheatsheets)|(sample)|(developer)|(-doc)|(-docs)|(-top)|(-demos)|(tutorial)|(awesome)|(must-watch)|(guide)|(interview)|(beginner)|(sample)|(leetcode)|(exercise)|(blog)|(china)|(learn)|(algorithms)|(lectures)|(workshop)|(tips)|(checklist).*$')

  filtered_topic_repos = pd.read_csv("statistic/left_repos_topic.csv")["Repo"]
  print(len(filtered_topic_repos))
  no_topic_repos = pd.read_csv("statistic/no_topic_repos.csv")["Repo"]
  print(len(no_topic_repos))
  repos = pd.concat([filtered_topic_repos, no_topic_repos], axis=0).unique().tolist()
  print(len(repos))
  filter_project_name = []
  for repo in repos:
    project = repo.split('/')[1].lower()
    username = repo.split('/')[0]
    if pattern.findall(project) or username in ["Tencent", "alibaba", "bilibili", "baidu", "pingcap","didi", 
                                                "youzan", "bytedance", "XiaoMi", "Meituan-Dianping",
                                                "NetEase"]:
      filter_project_name.append(repo)
  left_repos_project_name = [project for project in repos if project not in filter_project_name]
  filter_project_name = pd.DataFrame({"Repo": filter_project_name})
  filter_project_name.to_csv("statistic/filtered_project_name.csv", index=False)
  left_repos_project_name = pd.DataFrame({"Repo": left_repos_project_name})
  left_repos_project_name.to_csv("statistic/left_repos_project_name.csv")


def filter_specific_repo():
  specific_repos = pd.read_csv("statistic/specific_repos.csv")
  specific_repos = specific_repos["Repo"].unique().tolist()
  left_repos_project_name = pd.read_csv("statistic/left_repos_project_name.csv")["Repo"]
  left_repos = [repo for repo in left_repos_project_name if repo not in specific_repos]
  left_repos = pd.DataFrame({"Repo": left_repos})
  left_repos.to_csv("statistic/left_repos.csv", index=False)
  

def get_active_repo():
  repos = pd.read_csv("statistic/left_repos.csv")
  active_repo = []
  error = open("error_log.txt", mode="a+")
  for repo in repos["Repo"]:
    print(repo)
    url = f"https://api.github.com/repos/{repo}"
    try:
      response = requests.get(url, headers=HEADERS)
      response.raise_for_status()
      archive_status = response.json()["archived"]
      if not archive_status:
        active_repo.append(repo)
    except Exception as e:
      error.write(f"Encounter error at repo: {repo}\tMessage: {e}\n")
  error.close()
  active_repo = pd.DataFrame({"Repo": active_repo})
  active_repo.to_csv("statistic/left_active_repos.csv", index=False)


def check_chines_char(readme_content):
  html = markdown(readme_content)
  soup = BeautifulSoup(html, "html.parser")
  text = soup.get_text()
  total_char = len(text)
  chinese_char = 0
  for char in text:
    if u'\u4e00' <= char <= u'\u9fff':
      chinese_char += 1
  return chinese_char / total_char


def filter_chinese_project():
  repos = pd.read_csv("statistic/left_active_repos.csv")
  candidate = []
  error = open("error_log.txt", mode="a+")
  for repo in repos["Repo"]:
    print(repo)
    readme_content = None
    try:
      url = f"https://api.github.com/repos/{repo}/readme"
      response = requests.get(url, headers=HEADERS)
      response.raise_for_status()
      readme_url = response.json()["download_url"]
      response = requests.get(readme_url)
      response.raise_for_status()
      readme_content = response.content
    except Exception:
      error.write(f"Encounter error at repo: {repo}")  
    if readme_content:
      readme_content = readme_content.decode("utf-8")
      if check_chines_char(readme_content) >= 0.05:
        candidate.append(repo)
  error.close()
  valid_repos = [repo for repo in repos["Repo"] if repo not in candidate]
  candidate = pd.DataFrame({"Repo": candidate})
  candidate.to_csv("statistic/candidate.csv", index=False)
  valid_repos = pd.DataFrame({"Repo": valid_repos})
  valid_repos.to_csv("statistic/valid_repos.csv", index=False)


def rn_in_project():
  error_log = open("error_log.txt", "a+")
  repos = pd.read_csv("statistic/valid_repos.csv")
  has_release = {"Repo": [], "description": [], "created_at": [], "updated_at": [],
                 "pushed_at": [], "language": [], "default_branch": [], "num release": []}
  needed_info = ["description", "created_at", "updated_at", "pushed_at", "language", "default_branch"]
  no_release = []
  for repo in repos["Repo"]:
    print(repo)
    rns = None
    repo_info = None
    try:
      url = f"https://api.github.com/repos/{repo}"
      response = requests.get(url, headers=HEADERS)
      response.raise_for_status()
      response = response.json()
      repo_info = {key: response[key] for key in needed_info}
      rns = github_api(repo, "releases", func=lambda el: el)
    except Exception as e:
      error_log.write(f"Encounter error at repo: {repo}\tMessage: {e}\n")
    if not rns:
      no_release.append(repo)
    else:
      has_release["Repo"].append(repo)
      for key in needed_info:
        has_release[key].append(repo_info[key])
      has_release["num release"].append(len(rns))
      rns = pd.DataFrame(rns)
      rns.to_csv(f"statistic/release/{repo.replace('/', '_')}.csv")
    break

  print("Number of no release project is:", len(no_release))
  no_release = pd.DataFrame({"Repo": no_release})
  no_release.to_csv("statistic/no_release.csv", index=False)
  has_release = pd.DataFrame(has_release)
  has_release.to_csv("statistic/has_release.csv", index=False)


rn_in_project()