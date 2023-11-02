from subprocess import call, run, DEVNULL
import re
from time import time

class RepositoryManager:
    def __init__(self, project, commit_hash, parent_commit_family):
        self.project = project
        self.commit_hash = commit_hash
        self.parent_commit_family = parent_commit_family

    def get_repository_dir(self):
        return f"../projects/{self.project}"

    def get_output_dir(self):
        return f"output/{self.project}/{self.commit_hash}"

    def get_current_commit(self):
        return run('git rev-parse --verify HEAD', capture_output=True, shell=True, cwd=self.get_repository_dir()).stdout.decode("utf-8").strip('\n')

    def get_commit_list(self):
        cwd = self.get_repository_dir()
        call('git pull', shell=True, cwd=cwd, stdout=DEVNULL)
        main_branch = run('git branch', capture_output=True, shell=True, cwd=cwd).stdout.decode("utf-8").strip('\n').split('* ')[1]
        return run(f"git rev-list {main_branch} --first-parent", capture_output=True, shell=True, cwd=cwd, stdout=DEVNULL).stdout.decode("utf-8").split()

    def force_reset_to_specific_commit(self, commit_hash):
        start = time()
        call(f"git reset --hard {commit_hash}", shell=True, cwd=self.get_repository_dir())
        end = time()

        print(f"git command: {end - start}s")
        print(f"RESET TO {commit_hash}")

    def return_parents_if_merge_commit(self, commit_hash):
        parents = []
        is_merge = call(f"git cat-file -p {commit_hash} | grep ^parent[[:space:]][0-9a-f]",capture_output=True, shell=True, cwd=self.get_repository_dir()).stdout.decode("utf-8").split("\n")
        for parent in is_merge:
            if(re.search("^parent\s[0-9a-f]{40}",parent)):
                parent = parent.split()
                parents.append(parent[1])
        if len(parents) == 2:
            return parents

    def discover_fork_commits(self, commit_hash, parents):
        #temporario, verificar se pode dar problema
        merge_commit = call(f"git merge-base {parents[0]} {parents[1]}",capture_output=True,shell=True, cwd=self.get_repository_dir()).stdout.decode("utf-8").split("\n")
        return merge_commit[0]

