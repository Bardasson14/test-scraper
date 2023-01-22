# from datetime import date, timedelta
import requests
import json
import os, shutil, subprocess

class RepoManager:
    def __init__(self, minimum_stars, time_range):
        self.minimum_stars = minimum_stars
        self.time_range = time_range

    def execute_request(self):
        request = requests.post(
            'https://api.github.com/graphql',
            json={'query': self.get_query()},
            headers= {
                "Authorization": "Bearer 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"
            }
        )

        if request.status_code == 200:
            self.persist_repositories(request.json(), "repos.json")
        else:
            raise Exception("STATUS: {}-\nQUERY: {}".format(request.status_code, self.get_query()))
    

    def get_query(self):
        return """
            query {
                search(
                    type:REPOSITORY,
                    query: "%s",
                    last: 100
                ) 
                {
                    repos: edges {
                        repo: node {
                            ... on Repository {
                                url
                                name
                                description
                            }
                        }
                    }
                }
            }
        """ % self.get_search_params()

    def get_search_params(self):
        # TODO: incluir time range na filtragem
        return 'stars:>={} is:public language:Java sort:updated-desc'.format(self.minimum_stars)

    def persist_repositories(self, resp, file):
        with open(file, "w") as f:
            json.dump(resp, f, indent=4)

    def clone_all(self, file):
        repo_list = {}

        print("file: %s" % file)

        with open(file, "r") as f:
            repo_list = json.load(f)["data"]["search"]["repos"]

        for repo in repo_list[:5]:
            metadata = repo["repo"]

            dir = "./projects/{}".format(metadata["name"])

            if os.path.exists(dir):
                shutil.rmtree(dir)
            else:
                if not os.path.exists("./projects/"):
                    os.mkdir("./projects/")

            print("metadata: %s" % metadata)

            subprocess.call("git clone {}".format(metadata["url"]), shell=True, cwd="./projects/")

        return repo_list
