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
                with open(path, 'r') as f:
                    self.scraper.gather_test_info(f)
            else:
                with open(path, 'r') as f:
                    self.scraper.gather_method_info(f)

    def analyze_refactorings(self, commit_hash):
        output_dir = self.setup_output_folders(commit_hash)
        refactoring_miner_output_dir = f"{output_dir}/refactoring_miner.json"

        with open(refactoring_miner_output_dir, 'w+'):
            call(f"./RefactoringMiner-2.4.0/bin/RefactoringMiner -c /projects/{self.project} {commit_hash} -json {refactoring_miner_output_dir}", shell=True, cwd="/app")

        with open(refactoring_miner_output_dir, 'r') as f:
            output_json_data = load(f)
            refactorings = []

            if not output_json_data['commits']: return 
            selected_refactorings = filter(lambda r: r['type'] in ['Extract Method', 'Inline Method'], output_json_data['commits'][0]['refactorings'])
            
            for refactor in selected_refactorings:
                post_refactor_location = refactor['leftSideLocations'][0]
                method_signature = post_refactor_location['codeElement'].split()
                method_name = method_signature[1].split("(")[0]
                has_associated_test = self.check_if_method_has_associated_test(post_refactor_location['filePath'], method_name)
                
                refactorings.append([
                    refactor['type'],
                    post_refactor_location['filePath'],
                    post_refactor_location['startLine'],
                    post_refactor_location['endLine'],
                    has_associated_test
                ])

            if refactorings: print(refactorings)

            CsvWriterService(f"{output_dir}/refactorings.csv", 'w+').write_row([
                'TIPO',
                'ARQUIVO',
                'LINHA INICIAL', 
                'LINHA FINAL',
                'POSSUI TESTE?'
            ])

            CsvWriterService(f"{output_dir}/refactorings.csv", 'a').write_rows(refactorings)

    
    def check_if_method_has_associated_test(self, file_path, target_member): # target_member não é o suficiente

        class_name = file_path.split('/')[-1].split('.')[0]
        test_files = list(filter(lambda f: search(f"{class_name}Test", str(f.resolve()).split('/')[-1].split('.')[0]), Path(self.get_base_dir()).rglob('*.java')))

        for test_file in test_files:
            parsed_test_file = str(test_file.resolve())
            invocated_methods = call(f"java -jar JavaParser.jar {parsed_test_file}", shell=True, capture_output=True).stdout.decode('utf-8').split()
            # print(f"invocated methods {len(invocated_methods)}")
            # print(f"target_member: {target_member}")

            if invocated_methods:
                # print("entrou") 
                matching_invocations = list(filter(lambda m: search(f"{target_member}\s*\([^)]*\)", m), invocated_methods))
                # print(f"TARGET: {target_member}")
                # print(f"MATCHING: {matching_invocations}")

                if len(matching_invocations) > 0: 
                    return True

        return False


    def get_output_dir(self, commit_hash):
        return f"output/{self.project}/{commit_hash}"
    
    def setup_output_folders(self, commit_hash):
        return FileSystemService(self.project, commit_hash).create_output_dir()

    def analyze_codebase(self, commit_hash):
        # TODO: analisar commit imediatamente anterior

        repository_manager = RepositoryManager(self.project, None, [])
        repository_manager.force_reset_to_specific_commit(commit_hash)
        
        start = time()
        self.analyze_test_files()
        end = time()

        print(f"analisando arquivos de teste: {end-start}s")

        start = time()
        self.analyze_refactorings(commit_hash)
        end = time()
        print(f"analisando refatorações: {end-start}s")
# 
        # CsvWriterService(csv_output_dir, 'a').write_row([
        #     commit_hash,
        #     len(self.scraper.refactorings_found),
        #     len(self.scraper.methods_found),
        #     len(self.scraper.assertions_found),
        # ])

        self.scraper.clear_findings()