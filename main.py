import subprocess
from scraper import *
from utils import *

PROJECTS_DIR = '../projetos/'

TEST_COMMANDS = {
    'maven': 'mvn clean test',
    'gradle': './gradlew test'
}

if __name__ == "__main__":
    for project_dir in os.listdir(PROJECTS_DIR):
        full_dir = PROJECTS_DIR + project_dir
        analyze_test_directories(full_dir)
        project_root_files = os.listdir(full_dir)
        build_lib = get_build_lib(project_root_files, full_dir)

        if build_lib:
            subprocess.call(TEST_COMMANDS[build_lib], shell=True, cwd=full_dir)
        else:
            print("FRAMEWORK INCOMPATÍVEL!")

        # TODO: fix test running
        # TODO: run refactoringminer from here  