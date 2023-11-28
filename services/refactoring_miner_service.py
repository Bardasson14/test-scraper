from subprocess import run

class RefactoringMinerService:
    def __init__(self, project, commit_hash):
        self.project = project
        self.commit_hash = commit_hash

    def get_output_file_dir(self):
        return f"output/{self.project}/{self.commit_hash}/refactoring_miner_output.json"
         
    def execute(self):
        run(f"./RefactoringMiner-2.4.0/bin/RefactoringMiner -c projects/{self.project} {self.commit_hash} -json {self.get_output_file_dir()}", shell=True)

