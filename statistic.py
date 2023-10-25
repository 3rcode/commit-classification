import pandas as pd
import requests
from settings import HEADERS
import re
from markdown import markdown
from bs4 import BeautifulSoup
from make_data import github_api
import matplotlib.pyplot as plt
from typing import TypeVar
import chart_studio.plotly as plotly
import plotly.express as px
from collections import defaultdict
Markdown = TypeVar("Markdown")

def validate(rn: Markdown, valid_link_num: int = 1) -> bool:
  if pd.isna(rn):
      return False
  rn = str(rn)  
  pull_requests = re.findall(r"https:\/\/github.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/pull\/[0-9]+", rn)
  issues = re.findall(r"https:\/\/github.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/issues\/[0-9]+", rn)
  pr_issue = re.findall(r"\#[0-9]+\b", rn)  
  commits = re.findall(r"\b[0-9a-f]{7,40}\b", rn)
  return ((len(pull_requests) + len(commits) + len(issues) >= valid_link_num) or
          (len(pr_issue) + len(commits) >= valid_link_num))


def filter_string(text):
    """Filters the given string to remove all special escape sequences and links.
    Args:
        text: A string.
    Returns:
        A string with all special escape sequences and links removed.
    """
    # Remove all links.
    text = re.sub(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", '', text)
    # Remove all empty lines.
    text = re.sub(r'[\t\r\n\b\f\'\"\\]', '', text)
    return text


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
      error.write(f"Encounter error while get info of {repo}\tMessage: {e}\n")
  error.write("----------------------------------------------------------------------------------------------------\n")
  error.close()
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
  pattern = re.compile(r'^.*(\bcourse\b)|(book)|(interview)|(example)|(dataset)|(datasets)|(roadmap)|(cheat-sheet)|(cheatsheet)|(cheatsheets)|(sample)|(developer)|(-doc)|(-docs)|(-top)|(-demos)|(tutorial)|(awesome)|(must-watch)|(guide)|(beginner)|(leetcode)|(exercise)|(blog)|(china)|(learn)|(algorithms)|(lectures)|(workshop)|(tips)|(checklist).*$')

  filtered_topic_repos = pd.read_csv("statistic/left_repos_topic.csv")["Repo"]
  no_topic_repos = pd.read_csv("statistic/no_topic_repos.csv")["Repo"]
  repos = pd.concat([filtered_topic_repos, no_topic_repos], axis=0).unique().tolist()
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
  error.write("----------------------------------------------------------------------------------------------------\n")
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
    except Exception as e:
      error.write(f"Encounter error at repo: {repo}\tMessage: {e}\n")  
    if readme_content:
      readme_content = readme_content.decode("utf-8")
      if check_chines_char(readme_content) >= 0.05:
        candidate.append(repo)
  error.write("----------------------------------------------------------------------------------------------------\n")
  error.close()
  valid_repos = [repo for repo in repos["Repo"] if repo not in candidate]
  candidate = pd.DataFrame({"Repo": candidate})
  candidate.to_csv("statistic/candidate.csv", index=False)
  valid_repos = pd.DataFrame({"Repo": valid_repos})
  valid_repos.to_csv("statistic/valid_repos.csv", index=False)


def release_in_project():
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
      error_log.write(f"Encounter network related error at repo: {repo}\tMessage: {e}\n")
    if not rns:
      no_release.append(repo)
    else:
      has_release["Repo"].append(repo)
      for key in needed_info:
        has_release[key].append(repo_info[key])
      has_release["num release"].append(len(rns))
      rns = pd.DataFrame(rns)
      rns.to_csv(f"statistic/release/{repo.replace('/', '_')}.csv")
  no_release = pd.DataFrame({"Repo": no_release})
  print("Number of no release project is:", len(no_release))
  no_release.to_csv("statistic/no_release.csv", index=False)
  has_release = pd.DataFrame(has_release)
  print("Number of has release project is:", len(has_release))
  has_release.to_csv("statistic/has_release.csv", index=False)


def get_has_release_note_repo():
  has_release = pd.read_csv("statistic/has_release.csv")
  has_release["has_rn"] = [False] * len(has_release)
  for i in range(len(has_release)):

    print(has_release.loc[i, "Repo"])
    rns = pd.read_csv(f"statistic/release/{has_release.loc[i, 'Repo'].replace('/', '_')}.csv")
    for i in range(len(rns)):
      if not pd.isna(rns.loc[i, "body"]) and filter_string(rns.loc[i, "body"]):
        has_release.loc[i, "has_rn"] = True
        break
  has_release_note = has_release[has_release["has_rn"]]
  has_release_note.to_csv("statistic/has_release_note.csv", index=False)


def summarize_repos() -> None:   
  repos = pd.read_csv("statistic/has_release_note.csv")["Repo"]
  has_change_descriptor = pd.DataFrame(index=repos, columns=[1, 2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
  for repo in repos:
    print(repo)
    rns = pd.read_csv(f"statistic/release/{repo.replace('/', '_')}.csv")["body"]
    num_rn = num_rn_has_link = 0
    for rn in rns:
      if not pd.isna(rn) and filter_string(rn):
        num_rn += 1
        if validate(rn):
          num_rn_has_link += 1
    ratio_rn_has_link = num_rn_has_link / num_rn * 100
    for ratio in has_change_descriptor.columns:
      if ratio_rn_has_link >= ratio:
        has_change_descriptor.loc[repo, ratio] = 1
      else:
        has_change_descriptor.loc[repo, ratio] = 0
  has_change_descriptor.to_csv("statistic/has_change_descriptor.csv")


def get_timebw2rn():
  timebw2rn = []
  repos = pd.read_csv("statistic/has_release_note.csv")
  for repo in repos["Repo"]:
    print(repo)
    release_info = pd.read_csv(f"statistic/release/{repo.replace('/', '_')}.csv")
    release_info["created_at"] = pd.to_datetime(release_info["created_at"])
    release_info["year"] = release_info["created_at"].dt.year
    release_info = release_info.sort_values(by="created_at", ignore_index=True)
    if len(release_info) == 1:
      continue
    for idx in range(len(release_info) - 1):
      x = (release_info.loc[idx + 1, "created_at"] - release_info.loc[idx, "created_at"]).total_seconds()
      timebw2rn.append([repo, release_info.loc[idx + 1, "tag_name"], x / 3600 / 24, release_info.loc[idx + 1, "year"]])
  timebw2rn = pd.DataFrame(timebw2rn, columns=["Repo", "tag_name", "num days", "year"])
  timebw2rn.to_csv("statistic/timebw2rn.csv", index=False)


def get_no_link_release(year=2023):
  repos = pd.read_csv("statistic/has_release_note.csv")
  no_link_release = []
  for repo in repos["Repo"]:
    print(repo)
    rns = pd.read_csv(f"statistic/release/{repo.replace('/', '_')}.csv")  
    rns["created_year"] = pd.to_datetime(rns["created_at"]).dt.year  
    for i in range(len(rns)):
      if not validate(rns.loc[i, "body"]) and rns.loc[i, "created_year"] == year:
        no_link_release.append({"Repo": repo, 
                                "tag_name": rns.loc[i, "tag_name"], 
                                "created_at": rns.loc[i, "created_at"], 
                                "link": rns.loc[i, "html_url"]})
  no_link_release = pd.DataFrame(no_link_release, columns=["Repo", "tag_name", "created_at", "link"])
  no_link_release.to_csv(f"statistic/no_link_release_{year}.csv", index=False)


def run():
  # get_repo_topic()  # Get topics of repo
  # filter_topic()  # Filter out repos that has educational topics
  # filter_project_name()  # Filter out repos has project name contain educational keyword
  # filter_specific_repo()  # Filter out some specific repos (manually assess repos)
  # get_active_repo()  # Filter out archived repos
  # filter_chinese_project()  # Filter out projects not written in English
  # release_in_project()  # Get project that has release and release info
  get_has_release_note_repo()  # Get repo that has release note (some repo has release but not write release note)
  # summarize_repos()  # Summarize ratio of num release note has link and total num release note for all repositories
  # get_timebw2rn()


run()

