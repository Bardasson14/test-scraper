import subprocess
from scraper import *
from utils import *

PROJECTS_DIR = '../../projetos/'

TEST_COMMANDS = {
    'maven': 'mvn clean test -Denforcer.skip=true',
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
            cmd = f"./RefactoringMiner/build/distributions/RefactoringMiner-2.3.2/bin/RefactoringMiner -a ../../projetos/{project_dir}/ master -json ../{project_dir}.json"
            print(cmd)
            return_value = subprocess.call(cmd, shell=True)
       
	    
        else:
            print("FRAMEWORK INCOMPATÍVEL!")
	
        # TODO: fix test running
        # TODO: run refactoringminer from here  
