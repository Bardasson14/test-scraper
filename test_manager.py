from utils import *
from pathlib import Path
import os
import re
import subprocess

IMPORTS = ['import org.junit.*']
ANNOTATIONS = ['@Test', '@RunWith']
TEST_COMMANDS = {
    'maven': 'mvn clean test -Denforcer.skip=true',
    'gradle': './gradlew test'
}

class TestManager:

    def __init__(self): # TODO: mudar
        self.imports = IMPORTS
        self.annotations = ANNOTATIONS

    def run_test_suite(self, repository):
        root_dir = repository_dir(repository)
        build_lib = self.get_build_lib(repository)

        print("build_lib: %s" % build_lib)
        if build_lib:
            subprocess.call(TEST_COMMANDS[build_lib], shell=True, cwd=root_dir)
            subprocess.call("./refactoring_miner/bin/RefactoringMiner -a {} master -json {}.json".format(root_dir, root_dir))
        else:
            print("Suíte não encontrada para o Projeto %s" % repository)
    

    def get_test_files(self, repository):
        root_dir = repository_dir(repository)
        test_files = []

        for test_dir in scan_directories(root_dir):
            for path in Path(test_dir).rglob('*.java'):
                if re.search("Test", str(path.resolve()).split(".")[-2]): 
                    test_files.append(path)

        return test_files

    def get_build_lib(self, repository):
        root_dir = repository_dir(repository)
        root_files = os.listdir(root_dir)

        if 'pom.xml' in root_files:
            return 'maven'
        elif 'build.gradle' in root_files:
            return 'gradle'
        else:
            return None


