"""
Computes baseline extractive performance with LexRank.
Adaption of the sentence-transformers example to work with longer articles.
Notably, this also contains much longer input texts, which requires longer computation, due to square matrices.
"""

import os
from typing import List

import numpy as np
import pickle
import torch.cuda
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

from LexRank import degree_centrality_scores


def remove_empty_segments_and_headings(text):
    return [line.strip("\n ") for line in text if line.strip("\n ") and not line.startswith("=")]


def filter_short_segments(text, min_length):
    return [segment for segment in text if len(segment.split(" ")) >= min_length]


def compute_lexrank_sentences(model: SentenceTransformer, segments: List, device: str, num_segments: int):
    # Models will automatically run on GPU, even without device specification!
    embeddings = model.encode(segments, convert_to_tensor=True, device=device)

    self_similarities = cos_sim(embeddings, embeddings).cpu().numpy()

    centrality_scores = degree_centrality_scores(self_similarities, threshold=None, increase_power=True)

    # Use argpartition instead of argsort for faster sorting, since we only need k << n sentences.
    # most_central_indices = np.argsort(-centrality_scores)
    central_indices = np.argpartition(centrality_scores, -num_segments)[-num_segments:]

    # TODO: Figure out whether sorting makes sense here? We assume that Wikipedia has some sensible structure.
    #   Otherwise, reversing would be enough to get the job done and get the most similar sentences first.
    # Scores are originally in ascending order
    # list(most_central_indices).reverse()
    return sorted(list(central_indices))


def get_segmented_text(text, level="paragraph", filter_length=5):
    if level == "paragraph":
        segments = text.split("\n")
    elif level == "sentences":
        raise NotImplementedError("No sentence splitter implemented yet, please use 'paragraph' splitting.")
    else:
        raise ValueError("Unknown segmentation level specified! Please use either 'paragraph' or 'sentence'.")
    segments = remove_empty_segments_and_headings(segments)
    segments = filter_short_segments(segments, filter_length)
    return segments


def compute_median_character_compression_ratio(lang_data):
    """
    Use the training data to determine the median compression ratio of articles.
    """
    ratios = []
    for celex_id, texts in lang_data["train"].items():
        ratio = len(get_segmented_text(texts["reference_text"])) / len(get_segmented_text(texts["summary_text"]))
        ratios.append(ratio)
    return np.median(ratios)


def clean_celex_id(celex_id):
    # "/" is actually never encountered, but better safe than sorry.
    celex_id = celex_id.replace("/", "-")
    celex_id = celex_id.replace("(", "-")
    celex_id = celex_id.replace(")", "-")

    return celex_id


def compute_all_summaries():
    variant = "paragraph"  # Either "paragraph" or "sentence"

    device = "cuda:1" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2", device=device)

    with open("../Analysis/clean_data.pkl", "rb") as f:
        data = pickle.load(f)

    # # For debugging
    # data = {"english": data["english"]}

    for language, all_data in data.items():

        median_compression_ratio = compute_median_character_compression_ratio(all_data)

        for split, samples in all_data.items():
            for celex_id, sample in tqdm(samples.items()):

                # We only want to compute the lengths for training, not the embeddings
                if split == "train":
                    continue
                # For validation and test, compute the actual scores
                else:
                    segments = get_segmented_text(sample["reference_text"])
                    # Use the length of the current input text coupled with the average compression ratio as a guidance
                    expected_length = round(len(segments) / median_compression_ratio)
                    most_central_indices = compute_lexrank_sentences(model, segments, device, expected_length)

                    # Use ordered sentences, even if this does not exactly match the centrality scores
                    summary = [segments[idx] for idx in sorted(most_central_indices)]

                    out_path = os.path.join("./", variant, language, split)
                    os.makedirs(out_path, exist_ok=True)
                    with open(os.path.join(out_path, f"{clean_celex_id(celex_id)}.txt"), "w") as f:
                        f.write("\n".join(summary))

                    # Also write gold summaries as a reference for later
                    out_path = os.path.join("./", "gold", language, split)
                    os.makedirs(out_path, exist_ok=True)
                    with open(os.path.join(out_path, f"{clean_celex_id(celex_id)}.txt"), "w") as f:
                        f.write(sample["summary_text"])


if __name__ == '__main__':
    compute_all_summaries()
