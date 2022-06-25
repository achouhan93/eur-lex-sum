"""
Load the samples that are included in the submission
"""
import os
import json
import shutil

from lexrank_baselines import clean_celex_id

if __name__ == '__main__':
    with open("../Analysis/sample_data.json") as f:
        data = json.load(f)

    for language, all_data in data.items():
        for split, samples in all_data.items():
            # TODO: We could arguably fine-tune on this data?
            if split == "train":
                continue
            else:
                # for method in ["paragraph", "oracle", "lexrank",
                #                "./cross_lingual_baselines/translated"]:
                #     if method != "paragraph" and language != "spanish":
                #         continue
                #     if method == ""

                out_path = os.path.join("./generated_samples/", "paragraph", language, split)
                os.makedirs(out_path, exist_ok=True)
                for celex_id, _ in samples.items():
                    in_file = os.path.join("./paragraph", language, split, f"{clean_celex_id(celex_id)}.txt")
                    out_file = os.path.join(out_path, f"{clean_celex_id(celex_id)}.txt")
                    shutil.copyfile(in_file, out_file)

                    if language == "spanish":
                        print(f"{split}, {celex_id}")

                if language == "spanish":
                    for method in ["oracle", "translated", "lexrank"]:
                        out_path = os.path.join("./generated_samples/", "oracle", language, split)
                        os.makedirs(out_path, exist_ok=True)
                        for celex_id, _ in samples.items():
                            in_file = os.path.join("./cross_lingual_baselines/", method, "es", split,
                                                   f"{clean_celex_id(celex_id)}.txt")
                            out_file = os.path.join(out_path, f"{clean_celex_id(celex_id)}.txt")
                            shutil.copyfile(in_file, out_file)