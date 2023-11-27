from itertools import repeat
from utils import *
from code_analyzer import CodeAnalyzer
from concurrent import futures
import multiprocessing as mp
import pandas as pd

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

if __name__ == '__main__':
    with open('full_extract.csv') as f:
        csv_rows = pd.read_csv(f, header=0, chunksize=2000)
        df = pd.concat(csv_rows)
        df = df.iloc[34503:37593] # only mockito
        run_analysis((df))