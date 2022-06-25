"""
Simply rename files based on the cleaning function
"""

import os
import shutil

from sum_trans_baseline import clean_celex_id


def rename_files(root):
    for subdir, dirs, files in os.walk(root):
        for file in files:
            in_file = os.path.join(subdir, file)
            out_file = os.path.join(subdir, clean_celex_id(file))
            shutil.move(in_file, out_file)


if __name__ == '__main__':
    rename_files("./oracle")
    rename_files("./translated")
    rename_files("./lexrank")