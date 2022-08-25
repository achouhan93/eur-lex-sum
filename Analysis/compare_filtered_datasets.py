"""
Since there appears to be a (minor) discrepancy in the data after filtering for the rebuttal,
here is some more analysis of the two files.

UPDATE: it seems that the random shuffle is not entirely deterministic (despite setting a seed). This implies that
re-generated content might have different splits in terms of validation/test etc.?
"""

import pickle


if __name__ == '__main__':
    with open("clean_data.pkl", "rb") as f:
        data_new = pickle.load(f)
    with open("clean_data_backup.pkl", "rb") as f:
        data_old = pickle.load(f)

    # for (lang_old, all_data_old), (lang_new, all_data_new) in zip(data_old.items(), data_new.items()):
    #     print(f"Investigating {lang_old} and new data's {lang_new}")
    #     for (split_old, samples_old), (split_new, samples_new) in zip(all_data_old.items(), all_data_new.items()):
    #         # for (celex_id_old, sample_old), (celex_id_new, sample_new) in zip(samples_old.items(), samples_new.items()):
    #         for celex_id_old, sample_old in samples_old.items():
    #             if celex_id_old not in samples_new.keys():
    #                 print(f"{celex_id_old} no longer in the data set.")
    #         print(samples_new.keys())

    for (lang_old, all_data_old), (lang_new, all_data_new) in zip(data_old.items(), data_new.items()):
        assert lang_old == lang_new, "Language codes don't match"
        print(f"Procesing {lang_old} samples.")
        all_samples_old = {}
        for split, samples in all_data_old.items():
            all_samples_old.update(samples)

        all_samples_new = {}
        for split, samples in all_data_new.items():
            all_samples_new.update(samples)

        for celex_id_old, sample_old in all_samples_old.items():
            if celex_id_old not in all_samples_new.keys():
                print(f"{celex_id_old} no longer in {lang_old} samples.")
            else:
                # Compare the texts:
                if sample_old["reference_text"] != all_samples_new[celex_id_old]["reference_text"]:
                    print(f"Reference text for {celex_id_old} no longer match.")
                if sample_old["summary_text"] != all_samples_new[celex_id_old]["summary_text"]:
                    print(f"Summary text for {celex_id_old} no longer match.")
        print(f"All samples for {lang_old} processed.")