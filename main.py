from itertools import repeat
from utils import *
from code_analyzer import CodeAnalyzer
import csv
import time
from concurrent import futures
import multiprocessing as mp
import pandas as pd

# PROJECTS_DIR = '../projects/'
# ACCEPTED_PROJECTS = ['Activiti', 'antlr4', 'dbeaver', 'ExoPlayer', 'incubator-druid', 'incubator-shardingsphere', 'RxJava']
ACCEPTED_PROJECTS = ['Activiti']
def run_analysis_for_commit(df, row_index):
    row = df.iloc[row_index]
    project_name = row.iloc[1]
    print(f"LINHA {row_index} - {project_name}")
    
    if project_name in ACCEPTED_PROJECTS:
        analyzer = CodeAnalyzer(project_name)
        analyzer.analyze_codebase(row.iloc[0])

if __name__ == "__main__":
    with open('merge_refactoring_ds.csv') as f:
        csv_rows = pd.read_csv(f, header=1, chunksize=4000)
        df = pd.concat(csv_rows)

        start = time.time()

        for i in range(3500, 3800): #, len(df.index)):
            run_analysis_for_commit(df, i)

        end = time.time()
        
        print(f"Tempo total: {end - start}")