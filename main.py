from itertools import repeat
from utils import *
from code_analyzer import CodeAnalyzer
from concurrent import futures
import multiprocessing as mp
import pandas as pd
import argparse

def run_analysis(df, project):
    # for index, row in sub_data_frame.iterrows():
    CodeAnalyzer(project=project).analyze_codebase(df)

def main():
    parser = argparse.ArgumentParser()	
    parser.add_argument("--project", help="executed project") 
    args = parser.parse_args()

    with open(f"files/{args.project}.csv") as ds2_file:
        aux_csv_rows = pd.read_csv(ds2_file, header=0, chunksize=2000)
        aux_df = pd.concat(aux_csv_rows)
        selected_merge_commits_sha1 = list(set(aux_df.sha1.values.tolist()))

    print(selected_merge_commits_sha1)

    with open(f"files/{args.project}_branch.csv") as ds1_file:
        csv_rows = pd.read_csv(ds1_file, header=0, chunksize=2000)
        df = pd.concat(csv_rows)
        print(df.columns)
        df = df.query('sha1_merge_commit in @selected_merge_commits_sha1')
        run_analysis(df, args.project)

if __name__ == '__main__':
    main()