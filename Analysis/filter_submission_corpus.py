"""
Reduces the available files in the clean dataset to a manageable number per language,
such that we can submit it.
"""

import json
import pickle
from itertools import islice

from tqdm import tqdm


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


if __name__ == '__main__':
    with open("clean_data.pkl", "rb") as f:
        data = pickle.load(f)

    no_per_set = 5

    for language, all_data in tqdm(data.items()):
        for split, samples in all_data.items():
            data[language][split] = take(2, samples.items())

    with open("sample_data.json", "w") as f:
        json.dump(data, f, indent=2)
