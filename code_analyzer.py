from pathlib import Path
from re import search
import shutil
from code_scraper import CodeScraper
from repository_manager import RepositoryManager
from services.csv_writer_service import CsvWriterService
from utils import *
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
            run(f"./RefactoringMiner-2.4.0/bin/RefactoringMiner -c /projects/{self.project} {commit_hash} -json {refactoring_miner_output_dir}", shell=True, cwd="/app")
            
        with open(refactoring_miner_output_dir, 'r') as f:
            output_json_data = load(f)
            refactorings = []

            if not output_json_data['commits']: return 

            # TODO: exclude test refactorings
            for refactor in output_json_data['commits'][0]['refactorings']:
                if refactor['type'] in ['Extract Method', 'Inline Method']:
                    post_refactor_location = refactor['leftSideLocations'][0]
                    method_signature = post_refactor_location['codeElement'].split()
                    method_name = method_signature[1].split("(")[0]
                    has_associated_test = self.check_if_method_has_associated_test(method_name)
                    
                    refactorings.append([
                        refactor['type'],
                        post_refactor_location['filePath'],
                        post_refactor_location['startLine'],
                        post_refactor_location['endLine'],
                        has_associated_test
                    ])
                    # separate target member

            CsvWriterService(f"{output_dir}/refactorings.csv", 'w+').write_row([
                'TIPO',
                'ARQUIVO',
                'LINHA INICIAL', 
                'LINHA FINAL',
                'POSSUI TESTE?'
                # TODO: adicionar outras informações úteis
            ])
            CsvWriterService(f"{output_dir}/refactorings.csv", 'a').write_rows(refactorings)

    
    def check_if_method_has_associated_test(self, target_member): # target_member não é o suficiente
        for test_dir in get_directories_recursively(self.get_base_dir()):
            for path in Path(test_dir).rglob('*.java'):
                if search("Test", str(path.resolve()).split(".")[-2]):
                    invocated_methods = run(f"java -jar JavaParser.jar {path}", shell=True, capture_output=True).stdout.decode('utf-8').split()
                    matching_invocations = list(filter(lambda m: search(target_member, m), invocated_methods))
                    
                    if len(matching_invocations) > 0: 
                        print(f"MATCHING: {matching_invocations}")
                        return True
        
        return False


    def get_output_dir(self, commit_hash):
        return f"output/{self.project}/{commit_hash}"
    
    def setup_output_folders(self, commit_hash):
        return FileSystemService(self.project, commit_hash).create_output_dir()

    def analyze_codebase(self):
        repository_manager = RepositoryManager(self.project, None, [])
        commit_list = repository_manager.get_commit_list()
        csv_output_dir = f"output/{self.project}/history.csv"
        shutil.rmtree(csv_output_dir, ignore_errors=True)

        CsvWriterService(csv_output_dir, 'w+').write_row([
            'COMMIT',
            'REFATORAÇÕES',
            'MÉTODOS',
            'ASSERÇÕES'
        ])
        merge_commits = {}
        for commit_hash in commit_list[:100]:
            parents = repository_manager.return_parents_if_merge_commit(commit_hash) 

            if parents:
                fork_commit = repository_manager.discover_fork_commits(commit_hash, parents)
                merge_commits[commit_hash] = {
                    "parent_1": parents[0],
                    "parent_2": parents[1],
                    "fork_commit": fork_commit
                } 
            
            repository_manager.force_reset_to_specific_commit(commit_hash)
            
            self.analyze_test_files()
            self.analyze_class_files()
            self.analyze_refactorings(commit_hash)

            CsvWriterService(csv_output_dir, 'a').write_row([
                commit_hash,
                len(self.scraper.refactorings_found),
                len(self.scraper.methods_found),
                len(self.scraper.assertions_found),
                #TODO: ver outras informações úteis
            ])

            self.scraper.clear_findings()
        print(merge_commits)