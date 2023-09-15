from make_data import traverse_repos, build_rn_info, build_pr_info, build_cm_info, build_issue_info

if __name__ == "__main__":
    traverse_repos(build_rn_info)
