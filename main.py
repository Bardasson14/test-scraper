from utils import *
from code_analyzer import CodeAnalyzer
import os

PROJECTS_DIR = '../projects/'

TEST_COMMANDS = {
    'maven': 'mvn clean test -Denforcer.skip=true',
    'gradle': './gradlew test'
}

if __name__ == "__main__":
    for project_name in os.listdir(PROJECTS_DIR):
        analyzer = CodeAnalyzer(project_name)
        analyzer.analyze_codebase()