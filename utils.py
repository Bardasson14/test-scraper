from os import scandir

def repository_dir(repository):
    return "./projects/%s" % repository

def scan_directories(root_dir):
    return [f.path for f in scandir(root_dir) if f.is_dir()]