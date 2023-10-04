import javalang_custom
import itertools
from pathlib import Path
from utils import get_directories_recursively
from re import search

# TODO: add to dockerfile

def flatten_list(l):
    return list(itertools.chain.from_iterable(filter(lambda element : element is not None, l)))

def wanted_node_types():
    return [ javalang_custom.tree.MethodInvocation ]

# OBS.: separated loops for test purpose only
# collect all assertions

ROOT_DIR = "/home/vitor/tcc/jenkins"
all_dirs = get_directories_recursively(ROOT_DIR)
target_member = 'getThreshold'

has_associated_test = False
assertion_nodes = []

# TODO
# pass mocked refactoringminer input
# check if the method is actually tested

def check_if_has_associated_test():
    for test_dir in get_directories_recursively(ROOT_DIR):
        for path in Path(test_dir).rglob('*.java'):
            if search("Test", str(path.resolve()).split(".")[-2]):
                with open(path, 'r') as f:
                    try:
                        tree = javalang_custom.parse.parse(f.read())
                        for _, node in tree:
                            if type(node) in wanted_node_types():
                                if search('assert', node.member):
                                    invocation_nodes = filter(lambda n: type(n) == javalang_custom.tree.MethodInvocation, flatten_list(node.children))
                                    for invocation_node in invocation_nodes:
                                        if invocation_node.member == target_member:
                                            # print(path)
                                            # print(f"{invocation_node.qualifier}.{invocation_node.member}({invocation_node.arguments})")
                                            return True
                    except javalang_custom.parser.JavaSyntaxError as err:
                        print("Exception", err) # DESCONDIDERAR ERROS DE SINTAXE
    return False

check_if_has_associated_test()

            