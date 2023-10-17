import re
import pandas as pd
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

print(validate("""## What's Changed
* Fix error with lack of PosixPath support by @giff-h in https://github.com/django-extensions/django-extensions/pull/1785
* Import pkg_resources directly  by @foarsitter in https://github.com/django-extensions/django-extensions/pull/1782
* Add REMOTE_USER to werkzeug environment by @confuzeus in https://github.com/django-extensions/django-extensions/pull/1769
* runserver_plus template reloading by @foarsitter in https://github.com/django-extensions/django-extensions/pull/1775
* Add Python 3.11 support by @foarsitter in https://github.com/django-extensions/django-extensions/pull/1786
* Run tests againts Django 4.2 and add trove classifier by @michael-k in https://github.com/django-extensions/django-extensions/pull/1812
* fix: test_should_highlight_bash_syntax_without_name to include whites… by @foarsitter in https://github.com/django-extensions/django-extensions/pull/1797
* runserver_plus autoreload on template change by @foarsitter in https://github.com/django-extensions/django-extensions/pull/1796
* Add support for psycopg3 by @Apreche in https://github.com/django-extensions/django-extensions/pull/1814
* Fixed drop test database command with psycopg 3 by @jannh in https://github.com/django-extensions/django-extensions/pull/1818
* Fixed reset_db with psycopg3 (same patch like for drop_test_database) by @jannh in https://github.com/django-extensions/django-extensions/pull/1821
* Cleanup http: links by @Crocmagnon in https://github.com/django-extensions/django-extensions/pull/1798

## New Contributors
* @giff-h made their first contribution in https://github.com/django-extensions/django-extensions/pull/1785
* @foarsitter made their first contribution in https://github.com/django-extensions/django-extensions/pull/1782
* @confuzeus made their first contribution in https://github.com/django-extensions/django-extensions/pull/1769
* @Apreche made their first contribution in https://github.com/django-extensions/django-extensions/pull/1814
* @Crocmagnon made their first contribution in https://github.com/django-extensions/django-extensions/pull/1798

**Full Changelog**: https://github.com/django-extensions/django-extensions/compare/3.2.1...3.2.3"
""", 1))