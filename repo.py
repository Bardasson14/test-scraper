from datetime import date, timedelta
import requests
import json
import os
from dotenv import load_dotenv, find_dotenv

MIN_STARS=50
LAST_PUSH=(date.today() - timedelta(days=90)).strftime("%y-%m-%d") # últimos 3 meses

load_dotenv(find_dotenv())

headers = {
    "Authorization": "Bearer {}".format(os.environ.get('GITHUB_TOKEN'))
}

def run_query(query):
    request = requests.post(
        'https://api.github.com/graphql',
        json={'query': query},
        headers=headers
    )

    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("STATUS: {}-\nQUERY: {}".format(request.status_code, query))

search_params = 'stars:>={} is:public language:Java'.format(MIN_STARS)

query = """
    query {
        search(
            type:REPOSITORY,
            query: "%s",
            first: 100
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
    """ % search_params

result = run_query(query)
json_dict = {}

for repo in result['data']['search']['repos']:
    repo_metadata = repo['repo']
    key = repo_metadata['name']
    data = {
        "clone_url": "{}.git".format(repo_metadata['url']),
    }
    json_dict[key] = data


with open("repos.json", "w") as f:
    json.dump(json_dict, f, indent=4)
