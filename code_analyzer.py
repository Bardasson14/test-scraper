from pathlib import Path
from re import search
import shutil
from code_scraper import CodeScraper
from repository_manager import RepositoryManager
from services.csv_writer_service import CsvWriterService
from utils import *
from subprocess import run, call
from services.file_system_service import FileSystemService
from json import load
from time import time

class CodeAnalyzer:
    def __init__(self, project):
        self.project = project
        self.scraper = CodeScraper(project)

    def get_base_dir(self):
        return f"../projects/{self.project}"
    
    def analyze_test_files(self):
        for path in Path(self.get_base_dir()).rglob('*.java'):
            if search("Test", str(path.resolve()).split(".")[-2]):
                with open(path, 'r', errors='ignore') as f:
                    self.scraper.gather_test_info(f)
            else:
                with open(path, 'r', errors='ignore') as f:
                    self.scraper.gather_method_info(f)

    def analyze_refactorings(self, commit_hash, previous_commits):
        output_dir = self.setup_output_folders(commit_hash)
        refactoring_miner_output_dir = f"{output_dir}/refactoring_miner.json"
        
        with open(refactoring_miner_output_dir, 'w+'):
            call(f"./RefactoringMiner-2.4.0/bin/RefactoringMiner -c /projects/{self.project} {commit_hash} -json {refactoring_miner_output_dir}", shell=True, cwd="/app")

        with open(refactoring_miner_output_dir, 'r') as f:
            # saídas

            # SAÍDA PRINCIPAL - DATASET DO ANDRÉ
            # 1 - refatorações com teste (tested refactorings (total))
            # 2 - refatorações sem teste (untested refactorings (total))
            # 3 - (%) refatorações com teste (tested refactorings (%))
            # 4 - total de refatorações
            # 5 - custom metric (refactoring percentage change)
        
            # SAÍDA P/ COMMIT
            # 1 - tinha teste antes? (buscar commit imediatamente anterior)
            # 2 - tem teste agora?
            # 3 - tipo de refatoração
            # 4 - tinha teste antes? (como botar isso?)

            # TODO - refatorar isso 

            output_json_data = load(f)
            refactorings = []

            if not output_json_data['commits']: return 
            selected_refactorings = filter(lambda r: r['type'] in ['Extract Method', 'Inline Method'], output_json_data['commits'][0]['refactorings'])
            
            for refactor in selected_refactorings:
                pre_refactor_location =  refactor['leftSideLocations'][0]
                post_refactor_location = refactor['rightSideLocations'][0]
                
                previous_method_signature = pre_refactor_location['codeElement'].split() 
                method_signature = post_refactor_location['codeElement'].split()

                previous_method_name = previous_method_signature[1].split("(")[0]
                method_name = method_signature[1].split("(")[0]

                has_associated_test = self.check_if_method_has_associated_test(post_refactor_location['filePath'], method_name)
                had_associated_test = False
                
                for commit in previous_commits:
                    repository_manager = RepositoryManager(self.project, None, [])
                    repository_manager.force_reset_to_specific_commit(commit)
                    
                    if self.check_if_method_has_associated_test(pre_refactor_location['filePath'], previous_method_name):
                        had_associated_test = True
                        break

                refactorings.append([
                    refactor['type'],
                    post_refactor_location['filePath'],
                    post_refactor_location['startLine'],
                    post_refactor_location['endLine'],
                    has_associated_test,
                    had_associated_test
                ])

            if refactorings: 
                print(refactorings)
                self.scraper.refactorings_found = refactorings

            # CsvWriterService(f"{output_dir}/refactorings.csv", 'w+').write_row([
            #     'TIPO',
            #     'ARQUIVO',
            #     'LINHA INICIAL', 
            #     'LINHA FINAL',
            #     'POSSUI TESTE?',
            #     'POSSUÍA TESTE?'
            # ])
            # CsvWriterService(f"{output_dir}/refactorings.csv", 'a').write_rows(refactorings)

    def check_if_method_has_associated_test(self, file_path, target_member):
        class_name = file_path.split('/')[-1].split('.')[0]
        test_files = list(filter(lambda f: search(f"{class_name}Test", str(f.resolve()).split('/')[-1].split('.')[0]), Path(self.get_base_dir()).rglob('*.java')))

        print(f"TEST_FILES: {test_files}")
        print(f"TARGET_MEMBER: {target_member}")
        
        for test_file in test_files:
            parsed_test_file = str(test_file.resolve())
            invocated_methods = run(f"java -jar JavaParser.jar {parsed_test_file}", shell=True, capture_output=True).stdout.decode('utf-8').split()
            print(f"INVOCATED METHODS: {invocated_methods}")

            if invocated_methods:
                matching_invocations = list(filter(lambda m: search(f".{target_member}\s*\([^)]*\)", m), invocated_methods))
                print(f"MATCHING INVOCATIONS: {matching_invocations}")

                if len(matching_invocations) > 0: 
                    return True

        return False


    def get_output_dir(self, commit_hash):
        return f"output/{self.project}/{commit_hash}"
    
    def setup_output_folders(self, commit_hash):
        return FileSystemService(self.project, commit_hash).create_output_dir()

    def analyze_codebase(self, row, df):
        commit_hash = row['sha1']
        # previous_commits = [row['parent1'], row['parent2']]
        previous_commits = []
        repository_manager = RepositoryManager(self.project, None, [])
        repository_manager.force_reset_to_specific_commit(commit_hash)
        
        self.analyze_refactorings(commit_hash, previous_commits)
        print(self.scraper.refactorings_found)

        current_coverage = 0
        previous_coverage = 0
        coverage_diff = real_coverage_diff = 0

        if self.scraper.refactorings_found:
            current_coverage = len(list(filter(lambda x: x[-2], self.scraper.refactorings_found))) / len(self.scraper.refactorings_found)
            previous_coverage = len(list(filter(lambda x: x[-1], self.scraper.refactorings_found))) /  len(self.scraper.refactorings_found)
            coverage_diff = current_coverage - previous_coverage

            if previous_coverage:
                real_coverage_diff = current_coverage/previous_coverage - 1

        print(f"CURRENT COVERAGE: {current_coverage}")
        print(f"PREVIOUS COVERAGE: {previous_coverage}")
        print(f"COVERAGE DIFF: {coverage_diff}")
        print(f"REAL COVERAGE DIFF: {real_coverage_diff}")

        row = df.query(f"project_name=='{self.project}' & sha1=='{commit_hash}'")

        # df.iloc[row.index[0], -3] = f"{current_coverage * 100}%"
        # df.iloc[row.index[0], -2] = f"{previous_coverage * 100}%"
        # df.iloc[row.index[0], -1] = f"{'-' if coverage_diff < 0 else '+'}{coverage_diff*100}%"
        # df.to_csv('merge_refactoring_ds.csv')
        self.scraper.clear_findings()