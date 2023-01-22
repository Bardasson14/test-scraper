from dotenv import load_dotenv, find_dotenv
from utils import *
from datetime import date, timedelta

from repo_manager import RepoManager
from test_manager import TestManager

load_dotenv(find_dotenv())

MIN_STARS = 1000
LAST_PUSH = (date.today() - timedelta(days=90)).strftime("%y-%m-%d")

if __name__ == "__main__":
    repo_manager = RepoManager(MIN_STARS, LAST_PUSH)
    test_manager = TestManager()
    # repo_manager.execute_request()
    repo_list = repo_manager.clone_all("repos.json")
    for repository in repo_list[:3]:
        print("repository: %s" % repository)
        test_manager.run_test_suite(repository["repo"]["name"])


    