from typing import List, Dict, Union
import regex

import numpy as np


def clean_text(text: str) -> str:
    """
    Internally converts the text to a simple paragraph estimate, and re-joins it after simple cleaning operations.
    """

    split_text = get_split_text(text)

    # Remove empty lines and the XML identifier in some first line
    split_text = [line.strip() for line in split_text if line.strip() and not line.endswith(".xml")]
    # TODO: Merge and remove lines based on further heuristics to clean up
    # for line in split_text:
    #     # Check for short lines
    #     if len(line.split(" ")) < 4:
    #         # Skip the first line which contains a .xml file name
    #         if line.endswith(".xml"):
    #             continue
    #         # If digits are present, it is likely a match with the previous line
    #         elif regex.findall(r"[0-9]", line):
    #             continue
    #         # Or if we find other "item-like" characters, such as "a)" or "b)"
    #         elif regex.match(r"[a-z])", line):

    text = " ".join(split_text).replace("\n", " ")
    return text


def get_split_text(text: str) -> List[str]:
    """
    Utility function to generate pseudo-paragraph splitting
    """
    # Replace misplaced utf8 chars
    text = text.replace(u"\xa0", u" ")

    # Use two or more consecutive newlines as a preliminary split decision
    text = regex.sub(r"\n{2,}", r"[SPLIT]", text)
    split_text = text.split("[SPLIT]")
    return split_text


def compute_whitespace_split_length(text: str) -> int:
    return len(text.split(" "))


def print_language_stats(language: str,
                         reference_lengths: List[int],
                         summary_lengths: List[int],
                         compression_ratios: List[float]) -> None:
    print(f"#######################################\n"
          f"Stats for {language}:")
    print_dist(reference_lengths, "reference lengths")
    print_dist(summary_lengths, "summary lengths")
    print_dist(compression_ratios, "compression ratio")


def print_dist(lengths: List[Union[int, float]], description: str) -> None:
    print(f"Mean {description}:\t\t\t{np.mean(lengths):.2f} "
          f"+/- {np.std(lengths):.2f}")
    print(f"Median {description}:\t\t{np.median(lengths):.2f}")
    print(f"Minimum length of {description}:\t{np.min(lengths):.2f}\n"
          f"Maximum length of {description}:\t{np.max(lengths):.2f}\n\n")
