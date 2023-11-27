from inspect import currentframe
import re
from utils import *
from pathlib import Path

IMPORTS = ['import org.junit.*']
ANNOTATIONS = ['@Test', '@RunWith']

class CodeScraper:
    def __init__(self, project):
        self.project = project
        self.clear_findings()

    def clear_findings(self):
        self.refactorings_found = {}

    def find_imports(self, line, index):
        for regex in IMPORTS:
            found = re.search(regex, line)

            if found:
                self.imports_found.append("{} - line {}".format(line.strip(), index))

    def find_annotations(self, line, index):
        for regex in ANNOTATIONS:
            found = re.search(regex, line)

            if found:
                self.annotations_found.append("'{}' - line {}".format(line.strip(), index))
    
    def find_methods(self, line, index):
        REGEX = '(public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])'
        found = re.search(REGEX, line)

        if found:
            self.methods_found.append(("'{}' - line {}").format(line.strip(), index))
        
    def find_assertions(self, line, index):
        REGEX = "assert\w+\((.*?)\);" # TODO: revisar REGEX
        found = re.search(REGEX, line)

        if found:
            self.assertions_found.append(("'{}' - line {}").format(line.strip(), index))
        
    def gather_test_info(self, file):
        lines = file.readlines()
        for i in range(len(lines)):
            self.find_annotations(lines[i], i)
            self.find_imports(lines[i], i)
            self.find_assertions(lines[i], i)

    def gather_method_info(self, file):
        lines = file.readlines()
        for i in range(len(lines)):
            self.find_methods(lines[i], i)
