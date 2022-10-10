"""
Reduces the available files in the clean dataset to a manageable number per language,
such that we can submit it.
"""

import json
import pickle

from tqdm import tqdm


def take(n, dict_items):
    d = {}
    for idx, (k, v) in enumerate(dict_items):
        if idx >= n:
            return d
        d[k] = v


if __name__ == '__main__':
    with open("clean_data.pkl", "rb") as f:
        data = pickle.load(f)

    no_per_set = 2

    for language, all_data in tqdm(data.items()):
        for split, samples in all_data.items():
            data[language][split] = take(no_per_set, samples.items())

    with open("sample_data.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
