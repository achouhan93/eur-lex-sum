# Summarisation Task
import torch.cuda
import regex
from tqdm import tqdm
from transformers import *
import pickle

summarization_pipeline = pipeline('summarization', model="d0r1h/LEDBill", device=-1)

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
def get_translation_model_and_tokenizer(src, dst):
    """
    Given the source and destination languages, returns the appropriate model
    """
    # construct our model name
    model_name = f"Helsinki-NLP/opus-mt-{src}-{dst}"
    task_name = f"translation_{src}_to_{dst}"
    # initialize the tokenizer & model
    translator = pipeline(task_name, model = model_name, device=-1)
    return translator
    
translator_pipeline_fr = get_translation_model_and_tokenizer('en', 'fr')
translator_pipeline_de = get_translation_model_and_tokenizer('en', 'de')
translator_pipeline_es = get_translation_model_and_tokenizer('en', 'es')
translator_pipeline_it = get_translation_model_and_tokenizer('en', 'it')
translator_pipeline_pt = get_translation_model_and_tokenizer('en', 'pt')
translator_pipeline_nl = get_translation_model_and_tokenizer('en', 'nl')
translator_pipeline_da = get_translation_model_and_tokenizer('en', 'da')
translator_pipeline_el = get_translation_model_and_tokenizer('en', 'el')
translator_pipeline_fi = get_translation_model_and_tokenizer('en', 'fi')
translator_pipeline_sv = get_translation_model_and_tokenizer('en', 'sv')
translator_pipeline_ro = get_translation_model_and_tokenizer('en', 'ro')
translator_pipeline_hu = get_translation_model_and_tokenizer('en', 'hu')
translator_pipeline_cs = get_translation_model_and_tokenizer('en', 'cs')
translator_pipeline_pl = get_translation_model_and_tokenizer('en', 'pl')
translator_pipeline_bg = get_translation_model_and_tokenizer('en', 'bg')
translator_pipeline_sl = get_translation_model_and_tokenizer('en', 'sl')
translator_pipeline_et = get_translation_model_and_tokenizer('en', 'et')
translator_pipeline_lt = get_translation_model_and_tokenizer('en', 'lt')
translator_pipeline_sk = get_translation_model_and_tokenizer('en', 'sk')
translator_pipeline_mt = get_translation_model_and_tokenizer('en', 'mt')
translator_pipeline_hr = get_translation_model_and_tokenizer('en', 'hr')
translator_pipeline_ga = get_translation_model_and_tokenizer('en', 'ga')


def compute_all_crosslingualsummaries():
    with open("/Users/ashishchouhan/Desktop/Studies/6a. Production_Code/2. Main_University_Heidelberg_GitLab/1. Data Extraction/2022-eur-lex-sum/Code/Analysis/clean_data.pkl", "rb") as f:
        data = pickle.load(f)

    # English Text
    data = {"english": data["english"]}

    # Main Code
    for language, all_data in data.items():
        final_summary = {}
        for split, samples in all_data.items():
            if split == "train":
                continue
            else:
                for celex_id, sample in tqdm(samples.items()):               
                    cleaned_document = clean_text(sample["reference_text"])
                    tokenizer_kwargs = {'truncation':True,'max_length':16000, 'return_text':True}
                    summary = summarization_pipeline(cleaned_document, **tokenizer_kwargs)
                    summary_text = summary[0]['summary_text']
                    summary_dict = {}
                    summary_dict['systemSummary'] = summary_text
                    summary_dict['goldSummary'] = sample["summary_text"]
                    
                    translated_summary_de = translator_pipeline_de(summary_text, max_length=len(summary_text))
                    summary_dict['En2DeSum'] = translated_summary_de[0]['translation_text']

                    translated_summary_fr = translator_pipeline_fr(summary_text, max_length=len(summary_text))
                    summary_dict['En2FrSum'] = translated_summary_fr[0]['translation_text']

                    translated_summary_es = translator_pipeline_es(summary_text, max_length=len(summary_text))
                    summary_dict['En2EsSum'] = translated_summary_es[0]['translation_text']
                    
                    translated_summary_it = translator_pipeline_it(summary_text, max_length=len(summary_text))
                    summary_dict['En2ItSum'] = translated_summary_it[0]['translation_text']

                    translated_summary_pt = translator_pipeline_pt(summary_text, max_length=len(summary_text))
                    summary_dict['En2PtSum'] = translated_summary_pt[0]['translation_text']

                    translated_summary_nl = translator_pipeline_nl(summary_text, max_length=len(summary_text))
                    summary_dict['En2NlSum'] = translated_summary_nl[0]['translation_text']

                    translated_summary_da = translator_pipeline_da(summary_text, max_length=len(summary_text))
                    summary_dict['En2DaSum'] = translated_summary_da[0]['translation_text']

                    translated_summary_el = translator_pipeline_el(summary_text, max_length=len(summary_text))
                    summary_dict['En2ElSum'] = translated_summary_el[0]['translation_text']

                    translated_summary_fi = translator_pipeline_fi(summary_text, max_length=len(summary_text))
                    summary_dict['En2FiSum'] = translated_summary_fi[0]['translation_text']

                    translated_summary_sv = translator_pipeline_sv(summary_text, max_length=len(summary_text))
                    summary_dict['En2SvSum'] = translated_summary_sv[0]['translation_text']

                    translated_summary_ro = translator_pipeline_ro(summary_text, max_length=len(summary_text))
                    summary_dict['En2RoSum'] = translated_summary_ro[0]['translation_text']

                    translated_summary_hu = translator_pipeline_hu(summary_text, max_length=len(summary_text))
                    summary_dict['En2HuSum'] = translated_summary_hu[0]['translation_text']

                    translated_summary_cs = translator_pipeline_cs(summary_text, max_length=len(summary_text))
                    summary_dict['En2CsSum'] = translated_summary_cs[0]['translation_text']

                    translated_summary_pl = translator_pipeline_pl(summary_text, max_length=len(summary_text))
                    summary_dict['En2PlSum'] = translated_summary_pl[0]['translation_text']

                    translated_summary_bg = translator_pipeline_bg(summary_text, max_length=len(summary_text))
                    summary_dict['En2BgSum'] = translated_summary_bg[0]['translation_text']

                    translated_summary_sl = translator_pipeline_sl(summary_text, max_length=len(summary_text))
                    summary_dict['En2SlSum'] = translated_summary_sl[0]['translation_text']

                    translated_summary_et = translator_pipeline_et(summary_text, max_length=len(summary_text))
                    summary_dict['En2EtSum'] = translated_summary_et[0]['translation_text']

                    translated_summary_lt = translator_pipeline_lt(summary_text, max_length=len(summary_text))
                    summary_dict['En2LtSum'] = translated_summary_lt[0]['translation_text']

                    translated_summary_sk = translator_pipeline_sk(summary_text, max_length=len(summary_text))
                    summary_dict['En2SkSum'] = translated_summary_sk[0]['translation_text']

                    translated_summary_mt = translator_pipeline_mt(summary_text, max_length=len(summary_text))
                    summary_dict['En2MtSum'] = translated_summary_mt[0]['translation_text']

                    translated_summary_hr = translator_pipeline_hr(summary_text, max_length=len(summary_text))
                    summary_dict['En2HrSum'] = translated_summary_hr[0]['translation_text']

                    translated_summary_ga = translator_pipeline_ga(summary_text, max_length=len(summary_text))
                    summary_dict['En2GaSum'] = translated_summary_ga[0]['translation_text']

                    final_summary[celex_id] = summary_dict
                
                file_name = "abstractive_sumTrans_"+split+"_"+language+".pkl"
                final_file = open(file_name, "wb")
                pickle.dump(final_summary, final_file)
                final_file.close()

if __name__ == '__main__':
    compute_all_crosslingualsummaries()