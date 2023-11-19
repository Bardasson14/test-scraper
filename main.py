from itertools import repeat
from utils import *
from code_analyzer import CodeAnalyzer
from concurrent import futures
import multiprocessing as mp
import pandas as pd

ACCEPTED_PROJECTS = [
    "druid",
    "Activiti",
    "dropwizard",
    "flink",
    "gocd"
    "hadoop",
    "incubator-druid",
    "jenkins",
    "mockito",
    # "neo4j",
    "pinpoint",
    "realm-java",
    "redisson",
    "RxJava",
    "zaproxy"
]

def run_analysis(sub_data_frame, df):
    for index, row in sub_data_frame.iterrows():
        CodeAnalyzer(row['project_name']).analyze_codebase(row, df)

if __name__ == "__main__":
    with open('icse.csv') as f:
        csv_rows = pd.read_csv(f, header=0, chunksize=2000)
        df = pd.concat(csv_rows)
        
        print(df)

        df['current_coverage'] = "0%"
        df['previous_coverage'] = "0%"
        df['coverage_diff'] = "+0%"

        query_results = [df.query(f"project_name=='{project}'") for project in ACCEPTED_PROJECTS]

        with futures.ThreadPoolExecutor(max_workers=mp.cpu_count()) as executor:
            results = executor.map(run_analysis, query_results, repeat(df))
            for future in results: pass 