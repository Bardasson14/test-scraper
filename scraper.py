from inspect import currentframe
import re
from utils import *
from pathlib import Path

IMPORTS = ['import org.junit.*']
ANNOTATIONS = ['@Test', '@RunWith']

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

def find_methods(line, index):
    REGEX = '(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])'
    found = re.search(REGEX, line)

    if found:
        return ("'{}' - line {}").format(line.strip(), index)
    
def find_assertions(line, index):
    REGEX = 'assert\w+\((.*?)\);'
    found = re.search(REGEX, line)

    if found:
        return ("'{}' - line {}").format(line.strip(), index)

def gather_method_info(methods_found, line, index):
    method_found = find_methods(line, index)

    if method_found:
        methods_found.append(method_found)

    return methods_found

def gather_test_info(annotations_found, imports_found, assertions_found, line, index):

    annotation_found = find_annotations(line, index)
    import_found = find_imports(line, index)
    assertion_found = find_assertions(line, index)

    if annotation_found:
        annotations_found.append(annotation_found)

    if import_found:
        imports_found.append(import_found)
    
    if assertion_found:
        assertions_found.append(assertion_found)

    return annotations_found, imports_found, assertions_found

def display_results(results):
    for key, value in results.items():
        print("{} FOUND: {}".format(key, value))


def analyze_methods(file, found_methods):
    with open(file, 'r') as f:
        lines = f.readlines()

        methods_found = []

        for i in range(len(lines)):
            json_dict = { 'METHODS': [] }
            methods_found = gather_method_info(methods_found, lines[i], i)
            json_dict['METHODS'] = methods_found
        
        found_methods[f.name.split('/')[-1]] = json_dict

def analyze_tests(file, found_tests):
    with open(file, 'r') as f:
        lines = f.readlines()

        annotations_found = []
        imports_found = []
        assertions_found = []

        for i in range(len(lines)):
            annotations_found, imports_found, assertions_found = gather_test_info(annotations_found, imports_found, assertions_found, lines[i], i)

            json_dict = { 'ANNOTATIONS': [], 'IMPORTS': [], 'ASSERTIONS': [] }

            for found_annotation in annotations_found:
                json_dict['ANNOTATIONS'].append(found_annotation[0])

            for found_import in imports_found:
                json_dict['IMPORTS'].append(found_import[0])
            
            for found_assertion in assertions_found:
                json_dict['ASSERTIONS'].append(found_assertion)
        
        found_tests[f.name] = json_dict

def analyze_test_directories(base_dir, found_tests):
    for test_dir in get_test_directories(base_dir):
        for path in Path(test_dir).rglob('*.java'):
            if re.search("Test", str(path.resolve()).split(".")[-2]): 
                analyze_tests(path, found_tests) # path | content_lines| json_dict

def analyze_class_directories(base_dir, found_methods):
    for class_dir in get_test_directories(base_dir):
        for path in Path(class_dir).rglob('*.java'):
                analyze_methods(path, found_methods) # path | content_lines| json_dict

def get_build_lib(root_files, current_dir):
    if 'pom.xml' in root_files:
        return 'maven'
    elif 'build.gradle' in root_files:
        return 'gradle'
    else:
        return None

    
