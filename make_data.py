import os
import requests
import pygit2
import pandas as pd
import numpy as np
from settings import ROOTDIR, HEADERS, VALID_RN_NUM, VALID_LINK_NUM
from bs4 import BeautifulSoup
from markdown import markdown
from typing import List, Callable,  Tuple, TypeVar
import re


Time = TypeVar("Time")
Markdown = TypeVar("Markdown")

class MyRemoteCallbacks(pygit2.RemoteCallbacks):
    def transfer_progress(self, stats):
        print(f'{stats.indexed_objects}/{stats.total_objects}')


def valid(commit, lastest, oldest):
    return oldest.to_pydatetime().timestamp() <= commit.commit_time <= lastest.to_pydatetime().timestamp()


def crawl_repos(result_path: str) -> None:
    """ Crawl Github repo with highest star number 
        (Assume that the higher star number the higher project quality) 
        Store result in result_path """

    result = []
    for i in range(50):
        print(i + 1)
        resp = requests.get(f"https://gitstar-ranking.com/repositories?page={i + 1}")
        soup = BeautifulSoup(resp.text, "html.parser")
        repos_container = soup.find("div", {"class": "row"})
        repos = repos_container.find_all('a')
        for repo in repos:
            result.append('/'.join(repo["href"].split('/')[-2:]))       
    result = pd.DataFrame({"Repo": result})
    result.to_csv(result_path)


def filter_repos(input_path: str, result_path: str) -> None:
    candidates = pd.read_csv(input_path)
    commit_link = "https:\/\/github\.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/commit\/[a-zA-Z0-9]+"
    pr_link = "https:\/\/github\.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/pull\/[0-9]+"
    issue_link = "https:\/\/github\.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+\/issues\/[0-9]+"

    def validate(rn: Markdown) -> bool:
        if not rn:
            return False
        html = markdown(rn)
        soup = BeautifulSoup(html, "html.parser")
        all_a = soup.find_all('a')
        valid_link_num = 0
        for a in all_a:
            try:
                link = a["href"]
                if re.match(commit_link, link) or re.match(pr_link, link) or re.match(issue_link, link):
                    valid_link_num += 1
            except KeyError:
                continue
        if valid_link_num >= VALID_LINK_NUM:
            return True
        else:
            return False
        
    valid_repo = []
    for candidate in candidates["Repo"]:
        print(candidate)
        rns = github_api(candidate, "releases", func=lambda el: el["body"])
        if len(rns) <= VALID_RN_NUM: continue
        num_valid_rn = 0
        for rn in rns:
            if validate(rn):
                num_valid_rn += 1
        if num_valid_rn >= VALID_RN_NUM:
            valid_repo.append(candidate)
            df = pd.DataFrame({"Repo": valid_repo})
            df.to_csv(result_path)


def traverse_repos(repo_list_path: str, func: Callable[[str, str], None]) -> None:
    """ This function do func in range of all repositories in repo list file"""

    repos = pd.read_csv(repo_list_path)
    error_log = open("error_log.txt", "a+")
    for repo in repos["Repo"]:
        try:
            func(repo)
        except Exception as e:
            error_log.write((f"Repo {repo} encounter error: {e.message if hasattr(e, 'message') else e} "
                             f"in function {func.__name__}\n"))
    error_log.close()


def github_api(repo: str, type: str, func: Callable) -> List[str]:
    """ Get all specific component of element has type is type using github_api """

    page = 1
    all_els = []
    while True:
        url =f"https://api.github.com/repos/{repo}/{type}?per_page=100&page={page}"
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
        except requests.HTTPError as ex:
            print("Http error")
            break
        except requests.Timeout as ex:
            print("Timeout")
            break
        els = response.json()
        els_per_page = [func(el) for el in els]
        all_els += els_per_page
        # 100 is the limit of per_page param in github api
        if len(els) < 100:  
            break
        page += 1

    return all_els


def crawl_rn(repo: str) -> Callable[[str, str, str, Callable], List[str]]:
    """ Crawl all release notes at repo"""
    
    print(repo)
    func = lambda el: el
    
    return github_api(repo, type="releases", func=func)
    

def crawl_pr(repo: str) -> Callable[[str, str, str, Callable], List[str]]:
    """ Crawl all pull requests of repo """

    print(repo)
    func = lambda el: el
    
    return github_api(repo, type="pulls", func=func)
    

def crawl_issue(repo: str) -> Callable[[str, str, str, Callable], List[str]]:
    """ Crawl all issues of repo """

    print(repo)
    func = lambda el: el

    return github_api(repo, type="issues", func=func)


def crawl_cm(repo: str) -> List[str]:
    """ Crawl all commits in repo """

    folder = repo.replace('/', '_')
    path = os.path.join(ROOTDIR, "repos", folder)
    assert os.path.exists(path)
    cmd = f""" cd {path} 
            git branch -a"""
    all_branches = os.popen(cmd).read().split('\n')[:-1]
    all_branches = [branch.strip() for branch in all_branches if "HEAD ->" not in branch]
    all_commit_shas = set()
    for branch in all_branches[1:]:
        try:
            cmd = f"""cd {path} 
            git rev-list {branch}"""
            commit_shas = os.popen(cmd).read()
            # Each line is a commit sha and the last line is empty line
            commit_shas = commit_shas.split('\n')[:-1]
            all_commit_shas.update(commit_shas)
        except Exception:
            continue
    
    repo = pygit2.Repository(path)
    # Get commit message from commit sha
    commits = [repo.revparse_single(commit_sha) for commit_sha in all_commit_shas]
    
    # Get all commit message and commit sha
    commits = [
        {
            "message": commit.message, 
            "sha": commit.hex, 
            "author": commit.author, 
            "commit_time": commit.commit_time, 
            "committer": commit.committer
        } 
        for commit in commits 
    ]
    commits = pd.DataFrame(commits)
    return commits


def cm_spliter(message: str) -> Tuple[str, str]:
    """ Split commit into commit summary (the first line) and follow by commit description """
    
    try:
        # Convert markdown into html
        html = markdown(message)
        soup = BeautifulSoup(html, "html.parser")
        lines = [p.text.strip() for p in soup.find_all('p')]
        summary= lines[0]
        description = "<.> ".join(lines[1:])

        return summary, description
    except Exception:
        return None, None


def clone_repos(repo: str) -> None:
    """ Clone github repository """

    folder = repo.replace('/', '_')
    path = os.path.join(ROOTDIR, "repos", folder)
    pygit2.clone_repository(f"https://github.com/{repo}", path, callbacks=MyRemoteCallbacks())
    

def build_rn_info(repo: str) -> None:
    """ Get information of release notes at repo and store into a csv file at data/[repo] """

    folder = repo.replace('/', '_')
    try:
        # Crawl changelogs
        print("Start crawl release notes")
        rn_info = crawl_rn(repo)
        print("Crawl release notes done")
        assert rn_info is not None
        rn_info = pd.DataFrame(rn_info)
        folder_path = os.path.join(ROOTDIR, "data", folder)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        rn_info_path = os.path.join(folder_path, "rn_info.csv")
        rn_info.to_csv(rn_info_path)
    except Exception:
        print("Wrong implement")


def build_cm_info(repo: str) -> None:   
    """ Get information of commits at repo and store into a csv file at data/[repo] """
    
    folder = repo.replace('/', '_')
    print("Repo:", repo)
    try:
        folder_path = os.path.join(ROOTDIR, "data", folder)
        print("Start load commits")
        commits = crawl_cm(repo)
        print("Commits loaded")
        assert commits is not None
        # Get commit messages and commit descriptions
        summa_des = [cm_spliter(commit) 
                    for commit in commits.loc[:, "message"]]
        summaries, descriptions = zip(*summa_des)
        commit_df = pd.DataFrame({
            "Summary": summaries, 
            "Description": descriptions,
            "Sha": commits["sha"],
            "Author": commits["author"],
            "Committer": commits["committer"],
            "Commit Time": commits["commit_time"]
        })
        # Check commit messages
        print("Num commit messages:", len(commit_df))
        print("\n")
        print("==============================================")
        print("\n")
        commit_path = os.path.join(folder_path, "commit.csv")
        commit_df.to_csv(commit_path)
    except Exception as e:
        print("Wrong implemen at build_cm_info function")
        raise e


def build_pr_info(repo: str) -> None:
    """ Get information of pull requests at repo and store into a csv file at data/[repo] """

    folder = repo.replace('/', '_')
    try:
        # Crawl changelogs
        print("Start crawl pull requests")
        pr_info = crawl_pr(repo)
        print("Crawl pull requests done")
        assert pr_info is not None
        pr_info = pd.DataFrame(pr_info)
        folder_path = os.path.join(ROOTDIR, "data", folder)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        pr_info_path = os.path.join(folder_path, "pr_info.csv")
        pr_info.to_csv(pr_info_path)
    except Exception as e:
        print("Wrong implement at build_pr_info function")
        raise e


def build_issue_info(repo: str) -> None:
    """ Get information of release notes at repo and store into a csv file at data/[repo] """

    folder = repo.replace('/', '_')
    try:
        # Crawl changelogs
        print("Start crawl issues")
        issue_info = crawl_issue(repo)
        print("Crawl issues done")
        issue_info = pd.DataFrame(issue_info)
        folder_path = os.path.join(ROOTDIR, "data", folder)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        issue_info_path = os.path.join(folder_path, "issue_info.csv")
        issue_info.to_csv(issue_info_path)
    except Exception as e:
        print("Wrong implement at build_issue_info function")
        raise e


def make_data() -> None:
    # crawl_repos("raw_repos.csv")
    filter_repos("raw_repos.csv", "valid_repos.csv")
    traverse_repos("valid_repos.csv", clone_repos)
    traverse_repos("valid_repos.csv", build_rn_info)
    traverse_repos("valid_repos.csv", build_cm_info)
    traverse_repos("valid_repos.csv", build_pr_info)
    traverse_repos("valid_repos.csv", build_issue_info)