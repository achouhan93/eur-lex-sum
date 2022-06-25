# Summarisation Task
import torch.cuda
import os
import regex
from tqdm import tqdm
from functools import lru_cache
import pickle

from transformers import pipeline


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


def clean_celex_id(celex_id):
    # "/" is actually never encountered, but better safe than sorry.
    celex_id = celex_id.replace("/", "-")
    celex_id = celex_id.replace("(", "-")
    celex_id = celex_id.replace(")", "-")

    return celex_id


def clean_text(text):
    """
    Internally converts the text to a simple paragraph estimate, and re-joins it after simple cleaning operations.
    """

    split_text = get_split_text(text)

    # Remove empty lines and the XML identifier in some first line
    split_text = [line.strip() for line in split_text if line.strip() and not line.endswith(".xml")]
    text = " ".join(split_text).replace("\n", " ")
    return text


# Translation Task
@lru_cache(maxsize=1)
def get_translation_model_and_tokenizer(src, dst, device=-1):
    """
    Given the source and destination languages, returns the appropriate model
    """
    model_name = f"Helsinki-NLP/opus-mt-{src}-{dst}"
    task_name = f"translation_{src}_to_{dst}"
    translator = pipeline(task_name, model=model_name, device=device, batch_size=4)
    return translator


def generate_summary(pipe, text, max_length=4096):
    cleaned_document = clean_text(text)
    chunked_document = chunk_by_max_subword_length(cleaned_document, pipe.tokenizer, 16384)
    print(f"Cut document into {len(chunked_document)} chunks.")
    tokenizer_kwargs = {"truncation": True, "max_length": max_length, "return_text": True}
    summary = pipe(chunked_document, **tokenizer_kwargs)
    return "\n".join([segment["summary_text"] for segment in summary])


def chunk_by_max_subword_length(text, tokenizer, max_length=512):
    """
    Uses heuristics (or fallback) to split text into paragraphs approximately as long as the tokenizer allows.
    """
    # Try to split by paragraph-level
    paragraph_split = [split for split in text.split("\n") if split.strip("\t ")]
    # Ensure each one is shorter, otherwise split those again

    return obtain_splits(paragraph_split, tokenizer, max_length=max_length)


def obtain_splits(split, tokenizer, max_length, depth=0):
    final_splits = []
    current_buffer = ""
    current_buffer_len = 0
    for unit in split:
        # Record the subword length
        unit_length = len(tokenizer.encode(unit))
        # See if it is too long
        if unit_length > max_length:
            # Previous buffer definitely needs to be appended
            if current_buffer_len > 10:
                final_splits.append(current_buffer)
            # Also reset the buffer
            current_buffer = ""
            current_buffer_len = 0
            # And then recursively call this function again
            if depth == 1:
                approximate_sentence_split = unit.split(";")
            elif depth >= 2:
                approximate_sentence_split = unit.split(":")
                print(unit)
            else:
                approximate_sentence_split = unit.split(".")
            final_splits.extend(obtain_splits(approximate_sentence_split, tokenizer, max_length, depth=depth+1))

        # Otherwise, add the text to the current buffer if still possible
        else:
            # Extend by current buffer if it would otherwise be too long
            if current_buffer_len + unit_length >= max_length:
                if current_buffer_len > 10:
                    final_splits.append(current_buffer.rstrip(" "))
                # Reset buffer
                current_buffer = ""
                current_buffer_len = 0
            # In either case append current unit
            current_buffer += f"{unit} "
            current_buffer_len += unit_length + 1

    # Leftover last sample
    if current_buffer and current_buffer_len > 10:
        final_splits.append(current_buffer.rstrip(" "))

    return final_splits


def compute_all_crosslingual_summaries(pipeline, device=-1):
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
                    # Skip to only Maltese for now
                    if lang != "mt":
                        continue

                    translator_pipeline = get_translation_model_and_tokenizer("en", lang, device=device)
                    print(f"Processing {language} to {lang} summarization-translation:")
                    for idx, (celex_id, sample) in enumerate(tqdm(samples.items())):

                        summary_text = generate_summary(pipeline, sample["reference_text"])
                        chunked_summary = chunk_by_max_subword_length(summary_text, translator_pipeline.tokenizer, 500)
                        translated_summary = translator_pipeline(chunked_summary)

                        out_path = os.path.join("translated", lang, split)
                        os.makedirs(out_path, exist_ok=True)
                        with open(os.path.join(out_path, f"{clean_celex_id(celex_id)}.txt"), "w") as f:
                            f.write("\n".join([segment["translation_text"] for segment in translated_summary]))


if __name__ == "__main__":
    device = 1

    summarization_pipeline = pipeline("summarization", model="d0r1h/LEDBill", device=device)
    compute_all_crosslingual_summaries(summarization_pipeline, device=device)
