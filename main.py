from pathlib import Path
from scraper import *
from utils import *

if __name__ == "__main__":
    test_dirs = []

    for test_dir in get_test_directories():
        for path in Path(test_dir).rglob('*.java'):
            if re.search("Test", str(path.resolve()).split(".")[-2]): 
                print(path)
                analyze_file(path)
                print("------------------------------------------------------------------------------------------------------------------------------------------------")