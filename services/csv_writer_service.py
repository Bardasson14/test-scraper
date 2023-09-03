import csv

class CsvWriterService:
    def __init__(self, target_file_dir, mode):
        self.target_file_dir = target_file_dir
        self.mode = mode

    def write_row(self, row):
        with open(self.target_file_dir, self.mode) as f:
            csv.writer(f).writerow(row)

    def write_rows(self, rows):
        with open(self.target_file_dir, self.mode) as f:
            csv.writer(f).writerows(rows)
    