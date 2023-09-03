from shutil import rmtree
from os import makedirs

class FileSystemService:
    def __init__(self, project, commit_hash):
        self.project = project
        self.commit_hash = commit_hash

    def get_output_dir(self):
        return f"output/{self.project}/{self.commit_hash}"

    def create_output_dir(self):
        dir = self.get_output_dir()
        rmtree(dir, ignore_errors=True)
        makedirs(dir, exist_ok=True)
        return dir
