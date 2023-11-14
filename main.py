from itertools import repeat
from utils import *
from code_analyzer import CodeAnalyzer
from concurrent import futures
import multiprocessing as mp
import pandas as pd

ACCEPTED_PROJECTS = [
    # 'Anki-Android',
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
    'gephi',
    # 'gocd',
    # 'hadoop',
    # 'incubator-druid', 
    # 'incubator-shardingsphere',
    # 'jenkins',
    # 'libgdx',
    # 'netty',
    'nokogiri',
    # 'pinpoint',
    # 'processing',
    # 'realm-java',
    # 'redisson',
    # 'RxJava',
    # 'skywalking',
    # 'spring-framework',
    # 'zaproxy',
]

def run_analysis(sub_data_frame, df):
    for index, row in sub_data_frame.iterrows():
        CodeAnalyzer(row['project_name']).analyze_codebase(row['sha1'], df)

if __name__ == "__main__":
    with open('merge_refactoring_ds.csv') as f:
        csv_rows = pd.read_csv(f, header=0, chunksize=2000)
        df = pd.concat(csv_rows)

        df = df.iloc[:500]
        # todo generate random
        df['current_coverage'] = "0%"
        df['previous_coverage'] = "0%"
        df['coverage_diff'] = "+0%"

        query_results = [df.query(f"project_name=='{project}'") for project in ACCEPTED_PROJECTS]

        with futures.ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
            futures = executor.map(run_analysis, query_results, repeat(df))
            for future in concurrent.futures.as_completed(futures):
                pass

        # for project in ACCEPTED_PROJECTS:
        #     print(project)
        #     # query_result = 
        #     run_analysis(query_result, df)