from distutils.command.build import build
import re
from pathlib import Path
from repos import REPOSITORIES_LIST
from utils import *

IMPORTS = ['import org.junit.*']
ANNOTATIONS = ['@Test', '@RunWith']
PROJECTS_DIR = './projects/'

TEST_COMMANDS = {
    'maven': 'mvn clean test -Denforcer.skip=true',
    'gradle': './gradlew test'
}

def find_imports(line, index):
    imports_found = []

    for regex in IMPORTS:
        found = re.search(regex, line)

        if found:
            imports_found.append("{} - line {}".format(line.strip(), index))
    
    return imports_found

def find_annotations(line, index):

    annotations_found = []

    for regex in ANNOTATIONS:
        found = re.search(regex, line)

        if found:
            annotations_found.append("'{}' - line {}".format(line.strip(), index))

    return annotations_found

def gather_info(annotations_found, imports_found, line, index):

    annotation_found = find_annotations(line, index)
    import_found = find_imports(line, index)

    if annotation_found:
        annotations_found.append(annotation_found)

    if import_found:
        imports_found.append(import_found)

    return annotations_found, imports_found

def analyze_test_directories(base_dir):
    for test_dir in get_test_directories(base_dir):
        for path in Path(test_dir).rglob('*.java'):
            if re.search("Test", str(path.resolve()).split(".")[-2]): 
                print(path)
                analyze_file(path)
    print("\n")

def analyze_file(file):
    with open(file, 'r') as f:
        lines = f.readlines()

        annotations_found = []
        imports_found = []

        for i in range(len(lines)):
            annotations_found, imports_found = gather_info(annotations_found, imports_found, lines[i], i)

        display_results({
            "ANNOTATIONS": [a[0] for a in annotations_found],
            "IMPORTS": [i[0] for i in imports_found]
        })

def display_results(results):
    for key, value in results.items():
        print("{} FOUND: {}".format(key, value))

def get_build_lib(root_files):
    if 'pom.xml' in root_files:
        return 'maven'
    elif 'build.gradle' in root_files:
        return 'gradle'
    else:
        return None

def run_tests():
    for project_dir in os.listdir(PROJECTS_DIR):
        full_dir = PROJECTS_DIR + project_dir
        # analyze_test_directories(full_dir)
        project_root_files = os.listdir(full_dir)
        build_lib = get_build_lib(project_root_files)
        print("BUILD LIB: {}".format(build_lib))

        if build_lib:
            subprocess.call(TEST_COMMANDS[build_lib], shell=True, cwd=full_dir)
        else:
            print("FRAMEWORK INCOMPATÍVEL!")