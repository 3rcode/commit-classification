import os
from settings import ROOTDIR, CM, PR, IS, BOT
import pandas as pd
import numpy as np
from typing import TypeVar
from markdown import markdown
from bs4 import BeautifulSoup
import re


Markdown = TypeVar('Markdown')

repo_path = os.path.join(ROOTDIR, "valid_repos.csv")
repos = pd.read_csv(repo_path)

def rn_stats():
    def validate_rn(rn: Markdown, valid_link_num: int = None) -> int or bool:
        # if not rn:
        #     return False
        # html = markdown(rn)
        # soup = BeautifulSoup(html, "html.parser")
        # all_a = soup.find_all('a')
        # cnt = 0
        # for a in all_a:
        #     try:
        #         link = a["href"]
        #         if re.match(CM, link) or re.match(PR, link) or re.match(IS, link):
        #             cnt += 1
        #     except KeyError:
        #         continue
        # if not valid_link_num:
        #     return cnt
        # else:
        #     return cnt >= valid_link_num
        pass
    num_rn = []
    # release_has_link = []
    oldest = latest = []
    num_valid_rn = 0
    num_empty_rn = 0
    # bot_like_author = []
    # num_bot_author_rn = 0
    # num_miss_author_info = 0
    # suspicious_repo = []
    average_link_in_repo = []
    for repo in repos["Repo"]:
        print(repo)
        folder = os.path.join(ROOTDIR, "data", repo.replace('/', '_'))
        rn = pd.read_csv(os.path.join(folder, "rn_info_sorted.csv"))
        rn["published_at"] = pd.to_datetime(rn["published_at"])
        num_rn.append(len(rn))
        oldest.append(rn["published_at"].iloc[-1])
        latest.append(rn["published_at"].iloc[0])
        empty_rn = rn["body"].isnull()
        num_empty_rn += sum(empty_rn)
        # miss_author_info = rn["author"].isnull()
        # num_miss_author_info += sum(miss_author_info)
        # check_bot = False
        # total_link = 0
        for i in range(len(rn)):
            # if not miss_author_info[i]:
            #     author_info = eval(rn.loc[i, "author"])
            #     login = author_info["login"]
            #     if BOT.findall(login):
            #         bot_like_author.append(login)
            #         num_bot_author_rn += 1
            #         check_bot = True
            if not empty_rn[i]:
                release_note = rn.loc[i, "body"]
                if validate_rn(release_note, 3):
                    # release_has_link.append({"Repo": repo, "Tag": rn.loc[i, "tag_name"], "Time": rn.loc[i, "published_at"]})
                    num_valid_rn += 1
            # if not empty_rn[i]:
            #     release_note = rn.loc[i, "body"]
            #     total_link += validate_rn(release_note)
    release_has_link = pd.DataFrame(release_has_link, columns=["Repo", "Tag", "Time"])
    release_has_link = release_has_link.sort_values(by="Time", ignore_index=True)
    release_has_link.to_csv("release_has_link.csv")
        # average_link_in_repo.append(total_link / len(rn))             
        # if check_bot:
        #     suspicious_repo.append(repo)
    # oldest = [x.to_pydatetime() for x in oldest]
    # latest = [x.to_pydatetime() for x in latest]

    # num_rn = np.array(num_rn)
    # print("Total num release note:", np.sum(num_rn))
    # print("Mean num release note:", np.mean(num_rn))
    # print("Max num release note:", np.max(num_rn))
    # print("Min num release note:", np.min(num_rn))
    # print("Median num release note:", np.median(num_rn))
    # print("Oldest release note:", min(oldest))
    # print("Latest release note:", max(latest))
    # print("Num empty release note:", num_empty_rn)
    # print("Num release note has at least 3 link to change descriptor", num_valid_rn)
    # print("Num release note missing author info:", num_miss_author_info)
    # print("Num bot like release note author:", num_bot_author_rn)
    # bot_like_author = pd.DataFrame({"bot_like_author": bot_like_author})
    # bot_like_author.to_csv("bot_like_author_release_note.csv")
    # suspicious_repo = pd.DataFrame({"Suspicious repo": suspicious_repo})
    # suspicious_repo.to_csv("suspicious_repo.csv")
    # average_link_in_repo = pd.DataFrame({"Repo": repos["Repo"], "Average link": average_link_in_repo})
    # average_link_in_repo.to_csv("average_link_in_repo.csv")


def cm_stats():
    num_cm = 0
    num_empty_commit_message = 0
    num_bot_author_commit = 0
    bot_like_author = []
    num_miss_author_info = 0
    suspicious_commit = []
    for repo in repos["Repo"]:
        print(repo)
        folder = os.path.join(ROOTDIR, "data", repo.replace('/', '_'))
        commit_info = pd.read_csv(os.path.join(folder, "commit_sorted.csv"))
        num_cm += len(commit_info)
        empty_message = commit_info["Summary"].isnull()
        num_empty_commit_message += sum(empty_message)
        miss_author_info = commit_info["Author"].isnull()
        num_miss_author_info += sum(miss_author_info)
        check_bot = False
        for i in range(len(commit_info)):
            if not miss_author_info[i]:
                author = commit_info.loc[i, "Author"]
                if BOT.findall(author):
                    bot_like_author.append(author)
                    num_bot_author_commit += 1
                    check_bot = True
        if check_bot:
            suspicious_commit.append(repo)

    print("Total commit:", num_cm)
    print("Num empty commit message:", num_empty_commit_message)
    print("Num miss author info commit:", num_miss_author_info)
    print("Num bot like author commit:", num_bot_author_commit)
    bot_like_author = pd.DataFrame({"bot_like_author": bot_like_author})
    bot_like_author.to_csv("bot_like_author_commit.csv")
    suspicious_commit = pd.DataFrame({"Suspicious commit repo": suspicious_commit})
    suspicious_commit.to_csv("suspicious_commit_repo.csv")


def issue_stats():
    total_issue = 0
    bot_user_num = 0
    suspicious_issue_repo = []
    bot_like_user = set()
    for repo in repos["Repo"]:
        print(repo)
        folder = os.path.join(ROOTDIR, "data", repo.replace('/', '_'))
        issue_info = pd.read_csv(os.path.join(folder, "issue_info_sorted.csv"), dtype="object",
                                 engine="python", on_bad_lines="skip")
        miss_user_info = issue_info["user"].isnull()
        total_issue += len(issue_info)
        check_bot = False
        for i in range(len(issue_info)):
            if not miss_user_info[i]:
                user = issue_info.loc[i, "user"]
                if BOT.findall(user):
                    bot_like_user.add(user)
                    bot_user_num += 1
                    check_bot = True
        if check_bot:
            suspicious_issue_repo.append(repo)
    print("Total issue:", total_issue)
    print("Num issue has bot like user", bot_user_num)
    bot_like_user = pd.DataFrame({"bot_like_user": list(bot_like_user)})
    bot_like_user.to_csv("bot_like_user_issue.csv")
    suspicious_issue_repo = pd.DataFrame({"Suspicious issue repo": suspicious_issue_repo})
    suspicious_issue_repo.to_csv("suspicious_issue_repo.csv")


def pr_stats():
    total_pr = 0
    bot_user_num = 0
    suspicious_pr_repo = []
    bot_like_user = set()
    for repo in repos["Repo"]:
        print(repo)
        folder = os.path.join(ROOTDIR, "data", repo.replace('/', '_'))
        pr_info = pd.read_csv(os.path.join(folder, "pr_info_sorted.csv"), dtype="object",
                              engine="python", on_bad_lines="skip")
        miss_user_info = pr_info["user"].isnull()
        total_pr += len(pr_info)
        check_bot = False
        for i in range(len(pr_info)):
            if not miss_user_info[i]:
                user = pr_info.loc[i, "user"]
                if BOT.findall(user):
                    bot_like_user.add(user)
                    bot_user_num += 1
                    check_bot = True
        if check_bot:
            suspicious_pr_repo.append(repo)
    print("Total pr:", total_pr)
    print("Num pr has bot like user", bot_user_num)
    bot_like_user = pd.DataFrame({"bot_like_user": list(bot_like_user)})
    bot_like_user.to_csv("bot_like_user_pr.csv")
    suspicious_pr_repo = pd.DataFrame({"Suspicious pr repo": suspicious_pr_repo})
    suspicious_pr_repo.to_csv("suspicious_pr_repo.csv")


def statistic():
    release_has_link = pd.read_csv("release_has_link.csv")
    release_has_link["Time"] = pd.to_datetime(release_has_link["Time"])
    release_has_link["Year"] = release_has_link["Time"].dt.year
    print(release_has_link.groupby(by=["Year"])["Time"].count())
    # print(release_has_link.info())