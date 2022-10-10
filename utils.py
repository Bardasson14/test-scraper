import os

def get_test_directories(base_dir):
    return [f.path for f in os.scandir(base_dir) if f.is_dir()]
    
    #test_dirs = []
    #for path, dirs, files in os.walk(base_dir):
    #    for dir in dirs:
    #        if dir == "test":
    #            test_dirs.append(os.path.join(path, dir))
    
    
