from itertools import repeat
from utils import *
from code_analyzer import CodeAnalyzer
from concurrent import futures
import multiprocessing as mp
import pandas as pd

import cProfile

ACCEPTED_PROJECTS = [
    # 'Activiti',
    # 'antlr4',
    # 'arduino',
    # 'cas',
    # 'che',
    # 'dbeaver',
    # 'dropwizard',
    # 'druid',
    # 'elasticsearch',
    # 'ExoPlayer',
    # 'gephi',
    # 'gocd',
    # 'hadoop',
    # 'incubator-druid', 
    # 'incubator-shardingsphere',
    # 'jenkins',
    # 'libgdx',
    # 'netty',
    # 'nokogiri',
    # 'pinpoint',
    # 'processing',
    'realm-java',
    # 'redisson',
    # 'RxJava',
    # 'skywalking',
    # 'spring-framework',
    # 'zaproxy',
]

def run_analysis(sub_data_frame, df):
    for index, row in sub_data_frame.iterrows():
        print(f"INDEX: {index}")
        CodeAnalyzer(row['project_name']).analyze_codebase(row['sha1'], df)

if __name__ == "__main__":
    with open('merge_refactoring_ds.csv') as f:
        csv_rows = pd.read_csv(f, header=0, chunksize=2000)
        df = pd.concat(csv_rows)
        df['current_coverage'] = "0%"
        df['previous_coverage'] = "0%"
        df['coverage_diff'] = "+0%"

        print(df)

        for project in ACCEPTED_PROJECTS:
            print(project)
            query_result = df.query(f"project_name=='{project}'")
            run_analysis(query_result, df)