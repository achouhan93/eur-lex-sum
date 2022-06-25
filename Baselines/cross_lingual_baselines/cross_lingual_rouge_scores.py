"""
Script to evaluate all different languages
"""
from typing import IO, Dict
import os

from rouge_score.scoring import BootstrapAggregator
from rouge_score.rouge_scorer import RougeScorer


def directory_iterator(source_dir: str, target_dir: str) -> (IO, IO):
    for fn in sorted(os.listdir(source_dir)):
        in_fp = os.path.join(source_dir, fn)
        out_fp = os.path.join(target_dir, fn)

        yield in_fp, out_fp


def evaluate_directory(aggregator, scorer, pred_dir: str, gold_dir: str) -> None:
    """
    Adds ROUGE evaluations to the passed aggregator object, depending on the files in the prediction directory.
    :return: None
    """
    for pred_fp, gold_fp in directory_iterator(pred_dir, gold_dir):
        with open(gold_fp) as f:
            gold = "".join(f.readlines())
        with open(pred_fp) as f:
            pred = "".join(f.readlines())

        aggregator.add_scores(scorer.score(gold, pred))


def print_aggregate(result: Dict) -> None:
    output = ""
    for key, value_set in result.items():
        output += f"{value_set.mid.fmeasure * 100:.2f} & "
        print(f"----------------{key} ---------------------")
        print(f"Precision | "
              f"low: {value_set.low.precision * 100:5.2f}, "
              f"mid: {value_set.mid.precision * 100:5.2f}, "
              f"high: {value_set.high.precision * 100:5.2f}")
        print(f"Recall    | "
              f"low: {value_set.low.recall * 100:5.2f}, "
              f"mid: {value_set.mid.recall * 100:5.2f}, "
              f"high: {value_set.high.recall * 100:5.2f}")
        print(f"F1        | "
              f"low: {value_set.low.fmeasure * 100:5.2f}, "
              f"mid: {value_set.mid.fmeasure * 100:5.2f}, "
              f"high: {value_set.high.fmeasure * 100:5.2f}")
    print(f"----------------------------------------")
    print(output)


def get_scores(language, lang, system_folder, fast=False):

    language = "spanish"
    lang = "es"

    # Translation baseline
    for split in ["validation", "test"]:
        aggregator = BootstrapAggregator(confidence_interval=0.95)
        scorer = RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False)

        pred_dir = os.path.join(system_folder, lang, split)
        gold_dir = os.path.join("../gold/", language, split)
        evaluate_directory(aggregator, scorer, pred_dir=pred_dir, gold_dir=gold_dir)
        print("\n------------------------------------")
        print(f"  Results for {language} {split}")
        result = aggregator.aggregate()
        print_aggregate(result)


if __name__ == "__main__":

    print("Summarized and translated model")
    get_scores("spanish", "es", "./translated")
    print("Oracle translations")
    get_scores("spanish", "es", "./oracle")
    print("Lexrank translations")
    get_scores("spanish", "es", "./lexrank")


