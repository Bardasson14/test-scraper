from subprocess import run

class RepositoryManager:
    def __init__(self, project, commit_hash):
        self.project = project
        self.commit_hash = commit_hash

    def get_repository_dir(self):
        return f"../projects/{self.project}"

    def get_output_dir(self):
        return f"output/{self.project}/{self.commit_hash}"
    
    def get_current_commit(self):
        return run('git rev-parse --verify HEAD', capture_output=True, shell=True, cwd=self.get_repository_dir()).stdout.decode("utf-8").strip('\n')

    def get_commit_list(self):
        cwd = self.get_repository_dir()
        print(cwd)
        run('git fetch', capture_output=True, shell=True, cwd=cwd)
        return run('git rev-list master --first-parent', capture_output=True, shell=True, cwd=cwd).stdout.decode("utf-8").split()
    
    def force_reset_to_specific_commit(self, commit_hash):
        run(f"git reset --hard {commit_hash}", shell=True, cwd=self.get_repository_dir())
        run(f"git rev-parse HEAD {commit_hash}", shell=True, cwd=self.get_repository_dir())
