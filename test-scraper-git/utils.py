import os
import shutil
import subprocess
from repos import REPOSITORIES_LIST

def download_repos():
    for repo in REPOSITORIES_LIST:
        dir = "./projects/{}".format(repo["name"])

        if os.path.exists(dir):
            shutil.rmtree(dir)

        subprocess.call("git clone {}".format(repo["clone_url"]), shell=True, cwd="./projects/")

def get_test_directories(base_dir):
    return [f.path for f in os.scandir(base_dir) if f.is_dir()]