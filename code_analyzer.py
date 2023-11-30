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
        return f"projects/{self.project}"
    
    def analyze_test_files(self):
        for path in Path(self.get_base_dir()).rglob('*.java'):
            if search("Test", str(path.resolve()).split(".")[-2]):
                with open(path, 'r', errors='ignore') as f:
                    self.scraper.gather_test_info(f)
            else:
                with open(path, 'r', errors='ignore') as f:
                    self.scraper.gather_method_info(f)

    def analyze_refactorings(self, commit_hash, previous_commit_hash):
        output_dir = self.setup_output_folders(commit_hash)
        refactoring_miner_output_dir = f"{output_dir}/refactoring_miner.json"
        commit_list = list(self.scraper.refactorings_found.keys())
        commit_list.append(commit_hash)

        for previous_commit_hash in self.scraper.refactorings_found.keys():
            commit_distance = commit_list.index(commit_hash) - commit_list.index(previous_commit_hash)
            previous_refactorings = filter(lambda r: r['associated_test_commit'] is None, self.scraper.refactorings_found[previous_commit_hash])

            for refactor in previous_refactorings:
                if self.check_if_method_has_associated_test(refactor['refactor_info']['pre_refactor_location']['filePath'], refactor['refactor_info']['previous_method_name']):
                    refactor['associated_test_commit'] = commit_hash
                    refactor['commits_before_testing'] = commit_distance

        with open(refactoring_miner_output_dir, 'a+'):
            call(f"./RefactoringMiner-2.4.0/bin/RefactoringMiner -c projects/{self.project} {commit_hash} -json {refactoring_miner_output_dir}", shell=True)

        with open(refactoring_miner_output_dir, 'r') as f:
            output_json_data = load(f)
            refactorings = []

            if not output_json_data['commits']:
                self.scraper.refactorings_found[commit_hash] = []
                return

            selected_refactorings = filter(lambda r: r['type'] in ['Extract Method', 'Inline Method', 'Rename Method'], output_json_data['commits'][0]['refactorings'])

            for refactor in selected_refactorings:
                refactor_info = self.get_refactor_info(refactor)

                has_associated_test = self.check_if_method_has_associated_test(
                    refactor_info['post_refactor_location']['filePath'],
                    refactor_info['current_method_name']
                )

                had_associated_test = False # use parent commit
                repository_manager = RepositoryManager(self.project, None)
                repository_manager.force_reset_to_specific_commit(previous_commit_hash)
                
                if self.check_if_method_has_associated_test(refactor_info['pre_refactor_location']['filePath'], refactor_info['previous_method_name']):
                    had_associated_test = True

                refactorings.append({
                    'type': refactor['type'],
                    'refactor_info': refactor_info,
                    'had_associated_test_before_refactor': had_associated_test,
                    'associated_test_commit': commit_hash if has_associated_test else None,
                    'commits_before_testing': 0 if has_associated_test else None
                })

            self.scraper.refactorings_found[commit_hash] = refactorings

    def check_if_method_has_associated_test(self, file_path, target_member):
        class_name = file_path.split('/')[-1].split('.')[0]
        test_files = list(filter(lambda f: search(f"{class_name}Test", str(f.resolve()).split('/')[-1].split('.')[0]), Path(self.get_base_dir()).rglob('*.java')))

        for test_file in test_files:
            parsed_test_file = str(test_file.resolve())
            invocated_methods = run(f"java -jar JavaParser.jar {parsed_test_file}", shell=True, capture_output=True).stdout.decode('utf-8').split()

            if invocated_methods:
                matching_invocations = list(filter(lambda m: search(f".{target_member}\s*\([^)]*\)", m), invocated_methods))

                if len(matching_invocations) > 0: 
                    return True

        return False

    def get_refactor_info(self, refactor):
        pre_refactor_info = refactor['leftSideLocations'][0]
        post_refactor_info = refactor['rightSideLocations'][0]
        previous_method_signature = pre_refactor_info['codeElement'].split() 
        current_method_signature = post_refactor_info['codeElement'].split()
        
        if len(previous_method_signature) > 1:
            previous_method_name = previous_method_signature[1].split("(")[0]
        else:
            previous_method_name = previous_method_signature[0]

        if len(current_method_signature) > 1:
            current_method_name = current_method_signature[1].split("(")[0]
        else:
            current_method_name = current_method_signature[0]

        return {
            'pre_refactor_location': pre_refactor_info,
            'post_refactor_location': post_refactor_info,
            'previous_method_name': previous_method_name,
            'current_method_name':  current_method_name
        }

    def get_output_dir(self, commit_hash):
        return f"output/{self.project}/{commit_hash}"
    
    def setup_output_folders(self, commit_hash):
        return FileSystemService(self.project, commit_hash).create_output_dir()

    def analyze_codebase(self, df):
        current_type_branch = None
        current_merge_commit = None

        if os.path.exists(f"results/{self.project}.csv"):
            os.remove(f"results/{self.project}.csv")

        writer_service = CsvWriterService(f"results/{self.project}.csv", 'a+')
        writer_service.write_row([
            'commit_hash',
            'total_refactorings',
            'extract_method',
            'inline_method',
            'rename_method',
            'total_tests_before_refactorings',
            'total_tests_after_refactoring',
            'test_coverage_before_refactorings',
            'test_coverage_after_refactorings',
            'refactoring_coverage_impact',
            'avg_commits_before_testing',
            'sha1_merge_commit',
            'type_branch'
        ])

        for index, row in df.iterrows():
            if current_type_branch and current_type_branch != row['type_branch']: # branch aberta
                rows = []
                
                for entry in self.scraper.refactorings_found.items():
                    commit_sha1 = entry[0]
                    commit_refactorings = entry[1]
                    tested_refactorings = list(filter(lambda r: r['associated_test_commit'] is not None, commit_refactorings))

                    test_coverage_before_refactorings = 0.0
                    test_coverage_after_refactorings = 0.0
                    avg_commits_before_testing = 0.0
                    refactoring_coverage_impact = 0.0

                    previously_tested_methods = len(list(filter(lambda r: r['had_associated_test_before_refactor'], commit_refactorings)))
                    currently_tested_methods = len(list(filter(lambda r: r['associated_test_commit'] is not None, commit_refactorings)))
                
                    if len(commit_refactorings) > 0:

                        test_coverage_before_refactorings = len(list(filter(lambda r: r['had_associated_test_before_refactor'], commit_refactorings))) / len(commit_refactorings)
                        test_coverage_after_refactorings = len(list(filter(lambda r: r['associated_test_commit'] is not None, commit_refactorings))) / len(commit_refactorings)
                        refactoring_coverage_impact = test_coverage_after_refactorings - test_coverage_before_refactorings

                        if len(tested_refactorings) > 0:
                            avg_commits_before_testing = sum(filter(None, [r['commits_before_testing'] for r in tested_refactorings])) / len(tested_refactorings)

                    rows.append([
                        commit_sha1,
                        len(commit_refactorings),
                        len(list(filter(lambda r: r['type'] == 'Extract Method', commit_refactorings))),
                        len(list(filter(lambda r: r['type'] == 'Inline Method', commit_refactorings))),
                        len(list(filter(lambda r: r['type'] == 'Rename Method', commit_refactorings))),
                        previously_tested_methods,
                        currently_tested_methods,
                        test_coverage_before_refactorings,
                        test_coverage_after_refactorings,
                        refactoring_coverage_impact,
                        avg_commits_before_testing,
                        current_merge_commit,
                        current_type_branch
                    ])

                writer_service.write_rows(rows)
                self.scraper.clear_findings()

            current_type_branch = row['type_branch']
            current_merge_commit = row['sha1_merge_commit']
            commit_hash = row['sha1']
            repository_manager = RepositoryManager(row['name'], None)
            repository_manager.force_reset_to_specific_commit(commit_hash)
            
            self.analyze_refactorings(commit_hash, row['parent'])