# Summarisation Task
import os
from tqdm import tqdm
import pickle

from sum_trans_baseline import get_translation_model_and_tokenizer, chunk_by_max_subword_length, clean_celex_id


def compute_oracle_translated_summaries(device=-1):
    langs = ["es", "de", "fr", "it", "da", "nl", "pt", "ro", "fi", "sv", "bg", "el", "li", "hu", "cs", "et",
             "lt", "pl", "sk", "sl", "mt", "hr", "ga"]

    with open("../../Analysis/clean_data.pkl", "rb") as f:
        data = pickle.load(f)

    # TODO: This can be extended to the full dataset to get full 24-to-24 translation
    data = {"english": data["english"]}
    for language, all_data in data.items():
        for split, samples in all_data.items():
            # TODO: We could arguably fine-tune on this data?
            if split == "train":
                continue
            else:
                for lang in langs:
                    # Skip everything but Spanish for now
                    if lang != "es":
                        continue


                    translator_pipeline = get_translation_model_and_tokenizer("en", lang, device=device)
                    print(f"Processing {language} to {lang} summarization-translation:")
                    for idx, (celex_id, sample) in enumerate(tqdm(samples.items())):

                        if split == "validation":
                            continue
                        if split == "test" and idx < 114:
                            continue

                        with open(os.path.join("../paragraph/", language, split, f"{clean_celex_id(celex_id)}.txt"), "r") as f:
                            summary_text = "\n".join(f.readlines())
                        chunked_summary = chunk_by_max_subword_length(summary_text, translator_pipeline.tokenizer, 500)
                        translated_summary = translator_pipeline(chunked_summary)

                        out_path = os.path.join("lexrank", lang, split)
                        os.makedirs(out_path, exist_ok=True)
                        with open(os.path.join(out_path, f"{clean_celex_id(celex_id)}.txt"), "w") as f:
                            f.write("\n".join([segment["translation_text"] for segment in translated_summary]))


if __name__ == "__main__":
    device = 1

    compute_oracle_translated_summaries(device=device)
