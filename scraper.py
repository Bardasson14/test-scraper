import re

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

def gather_info(annotations_found, imports_found, line, index):

    annotation_found = find_annotations(line, index)
    import_found = find_imports(line, index)

    if annotation_found:
        annotations_found.append(annotation_found)

    if import_found:
        imports_found.append(import_found)

    return annotations_found, imports_found

def display_results(results):
    for key, value in results.items():
        print("{} FOUND: {}".format(key, value))


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

    
