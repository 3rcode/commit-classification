import os
from settings import ROOTDIR, CM, PR, IS, BOT
import pandas as pd
import numpy as np
from typing import TypeVar
from markdown import markdown
from bs4 import BeautifulSoup


Markdown = TypeVar('Markdown')

repo_path = os.path.join(ROOTDIR, "valid_repos.csv")
repos = pd.read_csv(repo_path)

def rn_stas():
    # num_rn = 0
    # oldest = latest = []

    # def validate_rn(rn: Markdown, valid_link_num: str) -> bool:
    #     if not rn:
    #         return False
    #     html = markdown(rn)
    #     soup = BeautifulSoup(html, "html.parser")
    #     all_a = soup.find_all('a')
    #     cnt = 0
    #     for a in all_a:
    #         try:
    #             link = a["href"]
    #             if re.match(CM, link) or re.match(PR, link) or re.match(IS, link):
    #                 cnt += 1
    #         except KeyError:
    #             continue
    #     return cnt >= valid_link_num

    # num_valid_rn = 0
    # num_empty_rn = 0
    bot_like_author = []
    num_bot_author_rn = 0
    num_miss_author_info = 0
    for repo in repos["Repo"]:
        print(repo)
        folder = os.path.join(ROOTDIR, "data", repo.replace('/', '_'))
        rn = pd.read_csv(os.path.join(folder, "rn_info_sorted.csv"))
        # rn["published_at"] = pd.to_datetime(rn["published_at"])
        # num_rn.append(len(rn))
        # oldest.append(rn["published_at"].iloc[-1])
        # latest.append(rn["published_at"].iloc[0])
        # empty_rn = rn["body"].isnull()
        # num_empty_rn += sum(empty_rn)
        miss_author_info = rn["author"].isnull()
        num_miss_author_info += sum(miss_author_info)
        for i in range(len(rn)):
            if not miss_author_info[i]:
                author_info = eval(rn.loc[i, "author"])
                login = author_info["login"]
                if BOT.findall(login):
                    bot_like_author.append(login)
                    num_bot_author_rn += 1
            # if not empty_rn[i]:
            #     release_note = rn.loc[i, "body"]
            #     if validate_rn(release_note, 3):
            #         num_valid_rn += 1

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
    print("Num release note missing author info:", num_miss_author_info)
    print("Num bot like release note author:", num_bot_author_rn)
    bot_like_author = pd.DataFrame({"bot_like_author": bot_like_author})
    bot_like_author.to_csv("bot_like_author_release_note.csv")
    

def cm_stats():
    num_cm = 0
    num_empty_commit_message = 0
    num_bot_author_commit = 0
    bot_like_author = []
    num_miss_author_info = 0
    for repo in repos["Repo"]:
        print(repo)
        folder = os.path.join(ROOTDIR, "data", repo.replace('/', '_'))
        commit_info = pd.read_csv(os.path.join(folder, "commit_sorted.csv"))
        num_cm += len(commit_info)
        empty_message = commit_info["Summary"].isnull()
        num_empty_commit_message += sum(empty_message)
        miss_author_info = commit_info["Author"].isnull()
        num_miss_author_info += sum(miss_author_info)
        for i in range(len(commit_info)):
            if not miss_author_info[i]:
                author = commit_info.loc[i, "Author"]
                if BOT.findall(author):
                    bot_like_author.append(author)
                    num_bot_author_commit += 1
    print("Total commit:", num_cm)
    print("Num empty commit message:", num_empty_commit_message)
    print("Num miss author info commit:", num_miss_author_info)
    print("Num bot like author commit:", num_bot_author_commit)
    bot_like_author = pd.DataFrame({"bot_like_author": bot_like_author})
    bot_like_author.to_csv("bot_like_author_commit.csv")

cm_stats()

