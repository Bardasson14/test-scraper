from pathlib import Path
from re import search
import shutil
from code_scraper import CodeScraper
from repository_manager import RepositoryManager
from services.csv_writer_service import CsvWriterService
from utils import get_directories_recursively
from subprocess import run
from services.file_system_service import FileSystemService
from json import load

class CodeAnalyzer:
    def __init__(self, project):
        self.project = project
        self.scraper = CodeScraper(project)

    def get_base_dir(self):
        return f"../projects/{self.project}"
    
    def analyze_test_files(self):
        for test_dir in get_directories_recursively(self.get_base_dir()):
            for path in Path(test_dir).rglob('*.java'):
                if search("Test", str(path.resolve()).split(".")[-2]):
                    with open(path, 'r') as f:
                        self.scraper.gather_test_info(f)

    def analyze_class_files(self):
        for class_dir in get_directories_recursively(self.get_base_dir()):
            for path in Path(class_dir).rglob('*.java'):
                with open(path, 'r') as f:
                    self.scraper.gather_method_info(f)

    def analyze_refactorings(self, commit_hash):
        output_dir = self.setup_output_folders(commit_hash)
        refactoring_miner_output_dir = f"{output_dir}/refactoring_miner.json"

        with open(refactoring_miner_output_dir, 'w+'):
            run(f"./RefactoringMiner-2.4.0/bin/RefactoringMiner -c /projects/{self.project} {commit_hash} -json {refactoring_miner_output_dir}", shell=True)
            
        with open(refactoring_miner_output_dir, 'r') as f:
            output_json_data = load(f)
            refactorings = []

            if not output_json_data['commits']: return 

            for refactor in output_json_data['commits'][0]['refactorings']:
                refactor_location = refactor['leftSideLocations'][0]
                refactorings.append([refactor['type'], refactor_location['filePath'], refactor_location['startLine'], refactor_location['endLine']])

            CsvWriterService(f"{output_dir}/refactorings.csv", 'w+').write_row([
                'TIPO',
                'ARQUIVO',
                'LINHA INICIAL', 
                'LINHA FINAL'
            ])
            CsvWriterService(f"{output_dir}/refactorings.csv", 'a').write_rows(refactorings)


    def get_output_dir(self, commit_hash):
        return f"output/{self.project}/{commit_hash}"
    
    def setup_output_folders(self, commit_hash):
        return FileSystemService(self.project, commit_hash).create_output_dir()

    def analyze_codebase(self):
        repository_manager = RepositoryManager(self.project, None)
        commit_list = repository_manager.get_commit_list()
        csv_output_dir = f"output/{self.project}/history.csv"
        shutil.rmtree(csv_output_dir, ignore_errors=True)

        CsvWriterService(csv_output_dir, 'w+').write_row([
            'COMMIT',
            'REFATORAÇÕES',
            'MÉTODOS',
            'ASSERÇÕES'
        ])

        for commit_hash in commit_list[:500]:
            repository_manager.force_reset_to_specific_commit(commit_hash)
            self.analyze_test_files()
            self.analyze_class_files()
            self.analyze_refactorings(commit_hash)

            CsvWriterService(csv_output_dir, 'a').write_row([
                commit_hash,
                len(self.scraper.refactorings_found),
                len(self.scraper.methods_found),
                len(self.scraper.assertions_found),
                # ver informações úteis
            ])

            self.scraper.clear_findings()