import shutil
from scraper import *
from utils import *
import json
import subprocess
import os

PROJECTS_DIR = '../projects/'

TEST_COMMANDS = {
    'maven': 'mvn clean test -Denforcer.skip=true',
    'gradle': './gradlew test'
}


def analyze_commit(project_name, commit_hash):
    # TODO: split into functions
    # TODO: make optimizations
    output_dir = f"output/{project_name}/{commit_hash}"
    full_dir = PROJECTS_DIR + project_name

    found_tests = {}
    found_methods = {}

    subprocess.run(f"git reset --hard {commit_hash}", shell=True, cwd=full_dir)
    subprocess.run(f"git rev-parse HEAD {commit_hash}", shell=True, cwd=full_dir)

    analyze_test_directories(full_dir, found_tests)
    analyze_class_directories(full_dir, found_methods)

    output_file_dir = f"{output_dir}/refactoring_miner_output.json"

    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)

    f1 = open(f"{output_dir}/test_locations.json", 'w')
    json.dump(found_tests, f1)
    f1.close()

    f2 = open(f"{output_dir}/method_locations.json", 'w')
    json.dump(found_methods, f2)
    f2.close()

    print('FULL DIR', full_dir)
    print('COMMIT SHA-1', commit_hash)
    f3 = open(f"{output_dir}/refactoring_miner_output.json", 'w')
    subprocess.run(f"./RefactoringMiner-2.4.0/bin/RefactoringMiner -c /projects/{project_name} {commit_hash} -json {output_file_dir}", shell=True)
    f3.close()
    
    total_tests = 0
    total_assertions = 0
    total_methods = 0

    for test_class in found_tests.keys():
        total_assertions += len(found_tests[test_class]['ASSERTIONS'])
        total_tests += len(found_tests[test_class]['ANNOTATIONS'])

    for prod_class in found_methods.keys():
        total_methods += len(found_methods[prod_class]['METHODS'])

    print(f"{project_name} [{commit_hash}]")
    print("TESTES: ", total_tests)
    print("MÉTODOS: ", total_methods)
    print("ASSERTIONS: ", total_assertions)


if __name__ == "__main__":
    for project_name in os.listdir(PROJECTS_DIR):
        full_dir = PROJECTS_DIR + project_name
        subprocess.run(f"git fetch", shell=True, cwd=full_dir)
        commit_hash = subprocess.run('git rev-parse --verify HEAD', capture_output=True, shell=True, cwd=full_dir).stdout.decode("utf-8").strip('\n')
        commit_list = subprocess.run('git rev-list master --first-parent', capture_output=True, shell=True, cwd=full_dir).stdout.decode("utf-8").split()

        analyze_commit(project_name, commit_hash)

        for commit_full_hash in commit_list[:10]:
            if commit_full_hash != commit_hash:
                analyze_commit(project_name, commit_full_hash)