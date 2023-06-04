from inspect import currentframe
import re
from pathlib import Path
import json

IMPORTS = ['import org.junit.*']
ANNOTATIONS = ['@Test', '@RunWith']

def find_imports(line, index):
    imports_found = []

    for regex in IMPORTS:
        found = re.search(regex, line)

        if found:
            imports_found.append("{}".format(line.strip()))
    
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
        annotations_found.append(annotation_found[0])

    if import_found:
        imports_found.append(import_found[0])

    return annotations_found, imports_found

def display_results(results):
    for key, value in results.items():
        print("{} FOUND: {}".format(key, value))


def analyze_file(lines,file_path,json_list):
    annotations_found = []
    imports_found = []

    for i in range(len(lines)):
        annotations_found, imports_found = gather_info(annotations_found, imports_found, lines[i], i)
    
    if len(annotations_found) > 0 or len(imports_found) > 0:
        index = len(json_list.keys())
        key = "file_" + str(index)
        data = {"file_path": file_path,
                "annotations": annotations_found,
                "number_of_annotations": len(annotations_found),
                "imports": imports_found,
                "number_of_imports": len(imports_found)}
        json_list[key]=data

    # display_results({
    #     "ANNOTATIONS": [a for a in annotations_found],
    #     "IMPORTS": [i for i in imports_found]
    # })


def get_build_lib(file_name):
    if 'pom.xml' == file_name:
        return 'maven'
    elif 'build.gradle' == file_name:
        return 'gradle'
    return None

    
