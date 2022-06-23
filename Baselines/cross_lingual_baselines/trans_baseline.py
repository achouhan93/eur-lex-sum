from transformers import *

def get_translation_model_and_tokenizer(src_lang, dst_lang):
  """
  Given the source and destination languages, returns the appropriate model
  See the language codes here: https://developers.google.com/admin-sdk/directory/v1/languages
  For the 3-character language codes, you can google for the code!
  """
  # construct our model name
  model_name = f"Helsinki-NLP/opus-mt-{src}-{dst}"
  # initialize the tokenizer & model
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
  # return them for use
  return model, tokenizer

src = "en"
dst = "de"

model, tokenizer = get_translation_model_and_tokenizer(src, dst)

# encode the text into tensor of integers using the appropriate tokenizer
inputs = tokenizer.encode(actual_summary, return_tensors="pt", max_length=512, truncation=True)

# generate the translation output using greedy search
greedy_outputs = model.generate(inputs)
# decode the output and ignore special tokens
translated_summary = tokenizer.decode(greedy_outputs[0], skip_special_tokens=True)

print(actual_summary, translated_summary)