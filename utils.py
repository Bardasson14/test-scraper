import os

def get_directories_recursively(base_dir):
    return [f.path for f in os.scandir(base_dir) if f.is_dir()]
