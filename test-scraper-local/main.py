from scraper import *
from utils import *
import json

PROJECTS_DIR = '../projects/'

TEST_COMMANDS = {
    'maven': 'mvn clean test -Denforcer.skip=true',
    'gradle': './gradlew test'
}

if __name__ == "__main__":
    for project_dir in os.listdir(PROJECTS_DIR):
        full_dir = PROJECTS_DIR + project_dir
        found_tests = {}
        found_methods = {}
        analyze_test_directories(full_dir, found_tests)
        analyze_class_directories(full_dir, found_methods)

        f1 = open('test_locations.json', 'w')
        json.dump(found_tests, f1)
        f1.close()

        f2 = open('method_locations.json', 'w')
        json.dump(found_methods, f2)
        f2.close()
        
        # OPTIMIZE

        total_tests = 0
        total_methods = 0

        for test_class in found_tests.keys():
            total_tests += len(found_tests[test_class]['ANNOTATIONS'])

        for prod_class in found_methods.keys():
            total_methods += len(found_methods[prod_class]['METHODS'])

        print("PROJETO: ", project_dir)
        print("TESTES: ", total_tests)
        print("MÉTODOS: ", total_methods)
