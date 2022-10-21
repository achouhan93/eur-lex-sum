## Cross-lingual Experiments
In our work, we limited ourselves to a Spanish-English cross-lingual experiment,
which represents a language pair with highly available resources and pre-trained models.

#### `cross_lingual_rouge_scores.py`
Despite the name, this script simply computes ROUGE scores for the result summaries, based on the available files.
Requires the `xxx_baseline.py` scripts to be run first.

#### `lexrank_baseline.py`
Translates existing LexRank-ST summary texts into another language.
Currently, only the English-to-Spanish language pair is enabled.

#### `oracle_baseline.py`
As a sanity-checking baseline, we translate the Gold summary;
similar to other baselines, only English-to-Spanish is currently enabled.

#### `sum_trans_baseline.py`
This pipeline utilizes the "summarize then translate" approach for the English-to-Spanish summarization task.
In particular, it uses a Pegasus model fine-tuned on the LEDBill dataset to perform summarization on the English document,
and then translates it to a Spanish summary.
This is by far the most costly approach.

#### `unify_file_names.py`
Some files were originally not renamed properly, which can be fixed with this script.
Running it does not break anything, but will help fix problems if you encounter them in comparing Celex IDs between different baselines.