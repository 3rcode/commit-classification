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
    

  print("Number of no release project is:", len(no_release))
  no_release = pd.DataFrame({"Repo": no_release})
  no_release.to_csv("statistic/no_release.csv", index=False)
  has_release = pd.DataFrame(has_release)
  has_release.to_csv("statistic/has_release.csv", index=False)


def filter_repos() -> None:     
  """ Filter repo follow some criteria:
  1. Has at least VALID_RN_NUM has at least VALID_LINK_NUM links that refer to change descriptor
  2. Release note written in English """
  def validate(rn: Markdown, valid_link_num: int) -> bool:
    if pd.isna(rn):
        return False
    rn = str(rn)  
    pull_requests = re.findall(r"https:\/\/github.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/pull\/[0-9]+", rn)
    issues = re.findall(r"https:\/\/github.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/issues\/[0-9]+", rn)
    pr_issue = re.findall(r"\#[0-9]+\b", rn)  
    commits = re.findall(r"\b[0-9a-f]{7,40}\b", rn)
    return ((len(pull_requests) + len(commits) + len(issues) >= valid_link_num) or
            (len(pr_issue) + len(commits) >= valid_link_num))

  repos = pd.read_csv("statistic/has_release.csv")["Repo"]
  change_descriptor = pd.DataFrame(index=repos, columns=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
  print(change_descriptor.info())
  for link_num in change_descriptor.columns:
    print("-------------------------------------------------------------------------------------")
    print(link_num)
    for repo in repos:
      print(repo)
      rns = pd.read_csv(f"statistic/release/{repo.replace('/', '_')}.csv")["body"]
      
      num_release = sum([validate(rn, link_num) for rn in rns])
      change_descriptor.loc[repo, link_num] = num_release
  
  change_descriptor.to_csv("statistic/change_descriptor.csv")


def get_timebw2rn():
  timebw2rn = {}
  repos = pd.read_csv("statistic/has_release.csv")
  for repo in repos["Repo"]:
    release_info = pd.read_csv(f"statistic/release/{repo.replace('/', '_')}.csv")
    release_info["created_at"] = pd.to_datetime(release_info["created_at"])
    release_info = release_info.sort_values(by="created_at", ignore_index=True)
    if len(release_info) == 1:
      continue
    x = 0
    for idx in range(len(release_info) - 1):
        x += (release_info.loc[idx + 1, "created_at"] - release_info.loc[idx, "created_at"]).total_seconds()
    timebw2rn[repo] = x / (len(release_info) - 1) / 3600 / 24
    
  
  timebw2rn = pd.DataFrame.from_dict(timebw2rn, orient="index", columns=["Num days"])
  timebw2rn.to_csv("statistic/timebw2rn.csv")

# def get_no_body_release_info():
#   repos = pd.read_csv("statistic/has_release.csv")
#   no_body_release = []
#   for repo in repos["Repo"]:
#     print(repo)
#     rns = pd.read_csv(f"statistic/release/{repo.replace('/', '_')}.csv")    
#     for i in range(len(rns)):
#       if pd.isna(rns.loc[i, "body"]):
#         no_body_release.append({"Repo": repo, "tag_name": rns.loc[i, "tag_name"], "created_at": rns.loc[i, "created_at"]})
#   no_body_release = pd.DataFrame(no_body_release, columns=["Repo", "tag_name", "created_at"])
#   no_body_release.to_csv("statistic/no_body_release.csv", index=False)

      
def get_no_link_release(year=2023):
  def validate(rn, valid_link_num: int) -> bool:
    if pd.isna(rn):
        return False
    rn = str(rn)  
    pull_requests = re.findall(r"https:\/\/github.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/pull\/[0-9]+", rn)
    issues = re.findall(r"https:\/\/github.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/issues\/[0-9]+", rn)
    pr_issue = re.findall(r"\#[0-9]+\b", rn)  
    commits = re.findall(r"\b[0-9a-f]{7,40}\b", rn)
    return ((len(pull_requests) + len(commits) + len(issues) >= valid_link_num) or
            (len(pr_issue) + len(commits) >= valid_link_num))

  repos = pd.read_csv("statistic/has_release_note.csv")
  no_link_release = []
  for repo in repos["Repo"]:
    print(repo)
    rns = pd.read_csv(f"statistic/release/{repo.replace('/', '_')}.csv")  
    rns["created_year"] = pd.to_datetime(rns["created_at"]).dt.year  
    for i in range(len(rns)):
      if not validate(rns.loc[i, "body"], 1) and rns.loc[i, "created_year"] == year:
        no_link_release.append({"Repo": repo, 
                                "tag_name": rns.loc[i, "tag_name"], 
                                "created_at": rns.loc[i, "created_at"], 
                                "link": rns.loc[i, "html_url"]})
  no_link_release = pd.DataFrame(no_link_release, columns=["Repo", "tag_name", "created_at", "link"])
  no_link_release.to_csv(f"statistic/no_link_release_{year}.csv", index=False)

def get_has_release_note_repo():
  def filter_string(text):
    """Filters the given string to remove all special escape sequences and links.

    Args:
      text: A string.

    Returns:
      A string with all special escape sequences and links removed.
    """

    # Remove all special escape sequences.
    text = re.sub(r'\\(?:[abfnrtv]|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4})$', '', text)

    # Remove all links.
    text = re.sub(r'^https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F]{2}))+$', '', text)

    # Remove all empty lines.
    text = re.sub(r'[\t\r\n\b\f\'\"\\]', '', text)

    return text

  has_release = pd.read_csv("statistic/has_release.csv")
  has_release["has_rn"] = [False] * len(has_release)
  for i in range(len(has_release)):
    print(has_release.loc[i, "Repo"])
    rns = pd.read_csv(f"statistic/release/{has_release.loc[i, 'Repo'].replace('/', '_')}.csv")["body"]
    for rn in rns:
      if not pd.isna(rn) and filter_string(rn):
        has_release.loc[i, "has_rn"] = True
        break
  has_release_note = has_release[has_release["has_rn"]]
  has_release_note.to_csv("statistic/has_release_note.csv", index=False)


def run():
  # get_repo_topic()
  # filter_topic()
  # filter_project_name()
  # filter_specific_repo()
  # get_active_repo()
  # filter_chinese_project()
  # filter_repos()
  # get_timebw2rn()
  get_no_link_release()
  # get_has_release_note_repo()


def something():
  num_link = 1
  def filter_string(text):
      """Filters the given string to remove all special escape sequences and links.

      Args:
        text: A string.

      Returns:
        A string with all special escape sequences and links removed.
      """

      # Remove all special escape sequences.
      text = re.sub(r'\\(?:[abfnrtv]|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4})$', '', text)

      # Remove all links.
      text = re.sub(r'^https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F]{2}))+$', '', text)

      # Remove all empty lines.
      text = re.sub(r'[\t\r\n\b\f\'\"\\]', '', text)

      return text

  def validate(rn, valid_link_num: int) -> bool:
      if pd.isna(rn):
          return False
      rn = str(rn)  
      pull_requests = re.findall(r"https:\/\/github.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/pull\/[0-9]+", rn)
      issues = re.findall(r"https:\/\/github.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/issues\/[0-9]+", rn)
      pr_issue = re.findall(r"\#[0-9]+\b", rn)  
      commits = re.findall(r"\b[0-9a-f]{7,40}\b", rn)
      return ((len(pull_requests) + len(commits) + len(issues) >= valid_link_num) or
              (len(pr_issue) + len(commits) >= valid_link_num))

  has_rn = pd.read_csv("statistic/has_release_note.csv")
  release_time = defaultdict(lambda: [0, 0])
  for repo in has_rn["Repo"]:
    if repo == "moby/buildkit":
      print(repo)
      release_info = pd.read_csv(f"statistic/release/{repo.replace('/', '_')}.csv")[["body", "created_at"]]
      release_info["created_at"] = pd.to_datetime(release_info["created_at"])
      release_info["year"] = release_info["created_at"].dt.year
      print(release_info.info())
      # for i in range(len(release_info)):
      #     if not pd.isna(release_info.loc[i, "body"]) and filter_string(release_info.loc[i, "body"]):
      #         release_time[release_info.loc[i, "year"]][0] += 1
      #         if validate(release_info.loc[i, "body"], num_link):
      #             release_time[release_info.loc[i, "year"]][1] += 1    

  result = defaultdict()
  for year in release_time:
      result[year] = round(release_time[year][1] / release_time[year][0] * 10000) / 100
  df = pd.DataFrame({"Year": result.keys(), "Release note has link ratio": result.values()})
  fig = px.bar(df, x="Year", y="Release note has link ratio")
  fig.show()
  # fig = plt.figure()
  # axes = fig.add_axes([0 , 0, 1, 1])
  # axes.bar(result.keys(), result.values())
  # axes.set_title("Ratio of release has link to change description by year")
  # plt.grid(visible=True, axis='y')
  # axes

something()

