import pandas as pd
import requests
from settings import HEADERS
import re
from markdown import markdown
from bs4 import BeautifulSoup
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
                                          "book", "learning", "lists", "checklist", "leetcode", "list",
                                          "scikit-learn", "interview", "demo", "guidelines", 
                                          "definition", "string-boot-examples", "docs", "udacity"])]
  filtered_repos = set(filtered["Repo"].unique().tolist())
  left_repos = origin_repos - filtered_repos
  filtered_repos = pd.DataFrame({"Repo": list(filtered_repos)})
  filtered_repos.to_csv("statistic/filtered_topic.csv", index=False)
  left_repos = pd.DataFrame({"Repo": list(left_repos)})
  left_repos.to_csv("statistic/left_repos_topic.csv", index=False)


def filter_project_name():
  pattern = re.compile(r'^.*(\bcourse\b)|(book)|(interview)|(example)|(dataset)|(datasets)|(roadmap)|(cheet-sheet)|(cheetsheet)|(sample)|(developer)|(-doc)|(-docs)|(-top)|(tutorial)|(awesome)|(must-watch)|(guide)|(interview)|(beginner)|(sample)|(leetcode)|(exercise)|(blog)|(china).*$')

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
  lst_repo = ["walter201230/Python",
              "Asabeneh/30-Days-Of-Python",
              "fangwei716/30-days-of-react-native",
              "soapyigu/Swift-30-Projects",
              "rwv/chinese-dos-games",
              "LiuBoyu/blockchain",
              "yinxin630/fiora",
              "aosabook/500lines",
              "shengxinjing/programmer-job-blacklist",
              "yichengchen/clashX",
              "zhiwehu/Python-programming-exercises",
              "wangzheng0822/algo",
              "allenwong/30DaysofSwift",
              "peng-zhihui/XUAN",
              "GokuMohandas/Made-With-ML",
              "rougier/numpy-100",
              "jackfrued/Python-100-Days",
              "girliemac/a-picture-is-worth-a-1000-words",
              "coells/100days",
              "tangqiaoboy/iOSBlogCN",
              "timqian/chinese-independent-blogs",
              "greatfire/wiki",
              "lining0806/PythonSpiderNotes",
              "postmanlabs/postman-app-support",
              "vicoyeh/pointers-for-software-engineers"
            ]
  

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
  repos = pd.read_csv("statistic/left_repos_project_name.csv")
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
  candidate = pd.DataFrame({"Repo": candidate})
  candidate.to_csv("statistic/candidate1.csv", index=False)
    

filter_chinese_project()