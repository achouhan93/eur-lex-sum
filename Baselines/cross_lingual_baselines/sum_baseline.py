"""
Computes baseline Sum-trans performance with LexRank.
Adaption of the sentence-transformers example to work with longer articles.
"""
from typing import List

import numpy as np
import pickle
import torch.cuda
from tqdm import tqdm
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import regex

def clean_text(text):
    """
    Internally converts the text to a simple paragraph estimate, and re-joins it after simple cleaning operations.
    """

    split_text = get_split_text(text)

    # Remove empty lines and the XML identifier in some first line
    split_text = [line.strip() for line in split_text if line.strip() and not line.endswith(".xml")]
    text = " ".join(split_text).replace("\n", " ")
    return text

def get_split_text(text):
    """
    Utility function to generate pseudo-paragraph splitting
    """
    # Replace misplaced utf8 chars
    text = text.replace(u"\xa0", u" ")

    # Use two or more consecutive newlines as a preliminary split decision
    text = regex.sub(r"\n{2,}", r"[SPLIT]", text)
    split_text = text.split("[SPLIT]")
    return split_text

def compute_all_summaries():
    variant = "paragraph"  # Either "paragraph" or "sentence"
    device = "cuda:1" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained("d0r1h/LEDBill")
    model = AutoModelForSeq2SeqLM.from_pretrained("d0r1h/LEDBill", return_dict_in_generate=True).to(device)

    with open("../Analysis/clean_data.pkl", "rb") as f:
        data = pickle.load(f)

    # For debugging
    data = {"english": data["english"]}
    SystemSummaries = []

    for language, all_data in data.items():
        for split, samples in all_data.items():
            final_summary = {}
            for celex_id, sample in tqdm(samples.items()):
                if split == "train":
                    continue
                else:
                    cleaned_document = clean_text(sample["reference_text"])
                    input_ids = tokenizer.encode_plus(
                       cleaned_document, add_special_tokens=True,
                       max_length=16384, truncation=True,
                       padding="max_length", return_tensors="pt"
                       ).input_ids.to(device)
                    global_attention_mask = torch.zeros_like(input_ids)
                    global_attention_mask[:, 0] = 1
                    
                    sequences = model.generate(input_ids, global_attention_mask=global_attention_mask).sequences
                    summary = tokenizer.batch_decode(sequences, skip_special_tokens=True)

                    summary_dict = {}
                    summary_dict['systemSummary'] = summary
                    summary_dict['goldSummary'] = sample["summary_text"]

                    final_summary[celex_id] = summary_dict

    final_file = open("data.json", "w")
    pickle.dump(final_summary, final_file)
    final_file.close()

if __name__ == '__main__':
    compute_all_summaries()
