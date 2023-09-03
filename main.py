from utils import *
from code_analyzer import CodeAnalyzer
import os

PROJECTS_DIR = '../projects/'

if __name__ == "__main__":
    for project_name in os.listdir(PROJECTS_DIR):
        analyzer = CodeAnalyzer(project_name)
        analyzer.analyze_codebase()