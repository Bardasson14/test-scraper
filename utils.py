import os
import itertools

def get_directories_recursively(base_dir):
    return [f.path for f in os.scandir(base_dir) if f.is_dir()]

def flatten_list(l):
    return list(itertools.chain.from_iterable(filter(lambda element : element is not None, l)))