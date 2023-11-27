from itertools import repeat
from utils import *
from code_analyzer import CodeAnalyzer
from concurrent import futures
import multiprocessing as mp
import pandas as pd
import argparse

'''
ACCEPTED_PROJECTS = [
    "Activiti",
    "dropwizard",
    "flink",
    "gocd",
    "hadoop",
    "mockito",
    "apm/pinpoint",
    "realm-java",
    "redisson",
    "RxJava",
    "zaproxy",
    "antlr4",
    "closure-compiler"
]
'''

def run_analysis(df):
    # for index, row in sub_data_frame.iterrows():
    CodeAnalyzer().analyze_codebase(df)

def main():
    parser = argparse.ArgumentParser()	
    parser.add_argument("--project", help="executed project") 
    args = parser.parse_args()
    file_name = "/files/" + args.project + ".csv" 

    with open(file_name) as f:
        csv_rows = pd.read_csv(f, header=0, chunksize=2000)
        df = pd.concat(csv_rows)
        run_analysis((df))

if __name__ == '__main__':
    main()