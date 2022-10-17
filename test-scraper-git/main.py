import github
import sys,os
from scraper_git import *
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

#github.enable_console_debug_logging()
if __name__ == "__main__":
    g = github.Github(os.environ.get("GITHUB_TOKEN"))
    build_lib = None
    if len(sys.argv) == 2:
        repo = g.get_repo(sys.argv[1])
        contents = repo.get_contents("")
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                path = file_content.path
                file_name = file_content.name
                if ".java" in file_name:
                    decoded_file_content_lines = file_content.decoded_content.decode("utf-8").split("\n")
                    print(f"\n{path}")
                    analyze_file(decoded_file_content_lines)
                elif build_lib == None:
                    build_lib=get_build_lib(file_name)

                    
    else:
        print("How to run\npython3 script.py user/repository\nExample: python3 script.py jenkinsci/jenkins") 

