import os

def get_test_directories():
    test_dirs = []
    for path, dirs, files in os.walk('../mockito'):
        for dir in dirs:
            if dir == "test":
                test_dirs.append(os.path.join(path, dir))

    
    return [f.path for f in os.scandir('../mockito/') if f.is_dir()]