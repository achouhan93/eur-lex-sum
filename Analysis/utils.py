from typing import List, Union, Optional, Tuple
import regex

from tqdm import tqdm
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Set larger font size for plots
matplotlib.rc('xtick', labelsize=18)
matplotlib.rc('ytick', labelsize=18)
matplotlib.rc('legend', fontsize=18)
# set LaTeX font
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'


def clean_text(text: str) -> str:
    """
    Internally converts the text to what we estimate to be paragraphs, and re-joins it after simple cleaning operations.
    """

    split_text = get_split_text(text)
    # Remove empty lines and the XML identifier in some first line
    split_text = [line.strip() for line in split_text if line.strip() and not line.endswith(".xml")]

    text = "\n".join(split_text)
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
    """
    Prints mean +/- std, median, min/max for reference length, summary length and compression ratios.
    """
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


def identify_document_scans(celex_ids: List[str], reference_texts: List[str], summary_texts: List[str]):
    """
    PDF scans are hard (if not impossible) to align, which is why we want to filter them out.
    Fortunately for us, there are some distinct strings in the text snippets which we can filter by.
    """
    ref_text_scans = []
    summ_text_scans = []
    # Filter documents that are likely document scans
    for celex_id, ref_text, summ_text in zip(celex_ids, reference_texts, summary_texts):
        if "[NEW PAGE]" in ref_text:
            print(f"{celex_id} contains [NEW PAGE] in the reference text")
            # print(ref_text[:500])
            ref_text_scans.append(celex_id)

        if "[NEW PAGE]" in summ_text:
            print(f"{celex_id} contains [NEW PAGE] in the summary text")
            # print(ref_text[:500])
            summ_text_scans.append(celex_id)

    print(f"{len(ref_text_scans)} reference texts are likely document scans.")
    print(f"{len(summ_text_scans)} summary texts are likely document scans.")


def print_short_percentiles(reference_token_lengths, summary_token_lengths):
    """
    Quick analysis wrt the shorter end of documents.
    """
    # Evaluate how many docs are potentially affected by "really short" documents:
    print(f"Length of shortest 5% of reference articles: {np.percentile(reference_token_lengths, 5)} tokens")
    print(f"Length of shortest 5% of *summary* articles: {np.percentile(summary_token_lengths, 5)} tokens")

    print(f"Length of shortest 10% of reference articles: {np.percentile(reference_token_lengths, 10)} tokens")
    print(f"Length of shortest 10% of *summary* articles: {np.percentile(summary_token_lengths, 10)} tokens")


def manual_review(celex_ids, reference_texts, reference_token_lengths):
    """
    Manual inspection of extremely short summaries.
    """
    for celex_id, ref_text, ref_length in zip(celex_ids, reference_texts, reference_token_lengths):
        if ref_length < 500:
            print(celex_id)
            print(ref_text)
            input("Press a button to continue...")


def identify_duplicates_by_text(celex_ids, reference_texts, summary_texts,
                                reference_token_lengths, summary_token_lengths):
    # Evaluate which fraction of docs is affected by multiple summaries
    more_than_two = []
    exactly_two = []
    no_summary_of_found = []
    for celex_id, ref_text, summ_text, ref_length, summ_length in zip(celex_ids, reference_texts, summary_texts,
                                                                      reference_token_lengths, summary_token_lengths):

        # Lazy match the section of interest
        # Matching more documents
        summary_of_segment = regex.search(r"(SUMMARY OF:?|ACT)(.*?)(SUMMARY|WHAT IS|WHAT ARE|WHAT DOES)",
                                          summ_text, regex.DOTALL)
        if summary_of_segment:
            group_text = summary_of_segment[2].strip("\n ")
            num_relevant_segments = len(group_text.split("\n\n\n"))

            if num_relevant_segments > 2:
                # print(f"{celex_id} has more than two reference documents")
                more_than_two.append(celex_id)
            elif num_relevant_segments == 2:
                # print(f"{celex_id} has exactly two reference documents")
                exactly_two.append(celex_id)
        else:
            no_summary_of_found.append(celex_id)

    print(f"{len(more_than_two)} documents have more than two reference documents.")
    print(f"{len(exactly_two)} documents have exactly two reference documents.")
    print(f"This makes {(len(more_than_two) + len(exactly_two)) / len(reference_texts) * 100:.2f}% of documents.")
    print(f"For {len(no_summary_of_found)} documents, no 'SUMMARY OF' section could be found.")


def identify_duplicates_by_equality(celex_ids, summary_texts, summary_token_lengths):
    # Figure out how many duplicate summaries we have in the corpus
    # This is quite inefficient (with O(N²) comparisons), particularly for long texts.
    # There is a different number of matches if we proxy by only using the length, which is why I would not recommend.
    duplicated_summaries = set()
    for celex_id, summ_text, summ_length in tqdm(zip(celex_ids, summary_texts, summary_token_lengths)):
        for other_celex_id, other_summ_text, other_summ_length in zip(celex_ids, summary_texts, summary_token_lengths):

            # SequenceMatcher is way too slow for the long docs
            # seq = SequenceMatcher(None, summ_text, other_summ_text)
            if celex_id != other_celex_id and summ_text == other_summ_text:  # seq.ratio() > 0.95:
                # print(f"{celex_id} and {other_celex_id} have the same summary")
                # Sort by celex ID to avoid adding the reverse later on.
                duplicated_summaries.add(celex_id)

    print(f"{len(duplicated_summaries)} texts are affected by duplicated summaries.")


def histogram_plot(lengths: List[Union[int, float]],
                   language: str,
                   type_of_lengths: str,
                   xlim: Optional[Union[List, Tuple]] = (0, 20000),
                   ylim: Optional[Union[List, Tuple]] = (0, 150),
                   bins: int = 20,
                   fp: str = "./Insights/histogram.png"
                   ):
    plt.hist(lengths, range=xlim, bins=bins, color='#1b9e77')
    plt.xlim(xlim)
    plt.ylim(ylim)

    # Mean and std lines
    plt.axvline(np.mean(lengths), color='k', linestyle='dashed', linewidth=2)
    plt.axvline(np.mean(lengths) - np.std(lengths), color='k', linestyle='dotted', linewidth=1)
    plt.axvline(np.mean(lengths) + np.std(lengths), color='k', linestyle='dotted', linewidth=1)
    # Median line
    plt.axvline(np.median(lengths), color='#d95f02', linestyle='solid', linewidth=2)

    # Title and save
    plt.savefig(fp, dpi=300)
    plt.show()
    plt.close()
