'''
usage: 从fast_align得到的双语词典里，过滤出合适的词典。 (消歧、停用词)
dict格式： src \t tgt \t freq
可以用shell下载并指定路径，从而达到任意lang过滤. 或整理到自己repo里面
stop words:
    zh: https://github.com/goto456/stopwords.git              stopwords/cn_stopwords.txt
    en: https://github.com/stopwords-iso/stopwords-en.git     stopwords-en/stopwords-en.txt
    de: https://github.com/stopwords-iso/stopwords-de.git
    fr: https://github.com/stopwords-iso/stopwords-fr
    es: https://github.com/stopwords-iso/stopwords-es.git
    vi: https://github.com/stopwords/vietnamese-stopwords.git
    ru: https://github.com/stopwords-iso/stopwords-ru

fast-text:
     wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin

    labels=['en', 'ru', 'de', 'fr', 'it', 'ja', 'es', 'ceb', 'tr', 'pt', 'uk', 'eo', 'pl', 'sv',
             'nl', 'he', 'zh', 'hu', 'ar', 'ca', 'fi', 'cs', 'fa', 'sr', 'el', 'vi', 'bg', 'ko',
             'no', 'mk', 'ro', 'id', 'th', 'hy', 'da', 'ta', 'hi', 'hr', 'sh', 'be', 'ka', 'te',
             'kk', 'war', 'lt', 'gl', 'sk', 'bn', 'eu', 'sl', 'kn', 'ml', 'mr', 'et', 'az', 'ms',
             'sq', 'la', 'bs', 'nn', 'ur', 'lv', 'my', 'tt', 'af', 'oc', 'nds', 'ky', 'ast', 'tl',
             'is', 'ia', 'si', 'gu', 'km', 'br', 'ba', 'uz', 'bo', 'pa', 'vo', 'als', 'ne', 'cy',
             'jbo', 'fy', 'mn', 'lb', 'ce', 'ug', 'tg', 'sco', 'sa', 'cv', 'jv', 'min', 'io', 'or',
             'as', 'new', 'ga', 'mg', 'an', 'ckb', 'sw', 'bar', 'lmo', 'yi', 'arz', 'mhr', 'azb',
             'sah', 'pnb', 'su', 'bpy', 'pms', 'ilo', 'wuu', 'ku', 'ps', 'ie', 'xmf', 'yue', 'gom',
             'li', 'mwl', 'kw', 'sd', 'hsb', 'scn', 'gd', 'pam', 'bh', 'mai', 'vec', 'mt', 'dv', 'wa',
             'mzn', 'am', 'qu', 'eml', 'cbk', 'tk', 'rm', 'os', 'vls', 'yo', 'lo', 'lez', 'so', 'myv',
             'diq', 'mrj', 'dsb', 'frr', 'ht', 'gn', 'bxr', 'kv', 'sc', 'nah', 'krc', 'bcl', 'nap',
             'gv', 'av', 'rue', 'xal', 'pfl', 'dty', 'hif', 'co', 'lrc', 'vep', 'tyv']
缺点：fasttext没有并行判断，效率低
'''
import os
import sys
import fasttext
import requests
import wget

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.write(''.join(res))
    print(f'write to {file} success.')


class StopWords(object):
    def __init__(self,src_lang,tgt_lang,model_path=None):
        self.model=self.build_model(model_path)
        self.labels=[label.replace('__label__', '') for label in self.model.labels]
        assert src_lang in self.labels and tgt_lang in self.labels, "source or target language not valid."
        self.src_lang=src_lang
        self.tgt_lang=tgt_lang
        self.stop_words={src_lang:[],tgt_lang:[]}

    def is_word_valid(self,word,lang):
        assert lang==self.src_lang or lang==self.tgt_lang
        flag=True
        if word in self.stop_words[lang]:
            flag=False
        return flag

    def get_lang_ids(self,word_list):
        labels, scores = self.model.predict(word_list)
        lang_ids = [label[0].replace('__label__', '') for label in labels]
        return lang_ids

    def load_words(self,lang,file_path=None):
        assert lang==self.src_lang or lang==self.tgt_lang,"language not valid."
        if file_path is not None:
            lines=read_file(file_path)
            lines=[line.strip() for line in lines]
            self.stop_words[lang].extend(lines)
            print(f"Loaded {len(lines)} stop words for language: {lang}.")
        else:
            print(f"Stopwords file path should be None.")

    def build_model(self,model_path=None):
        if model_path is  None:
            url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
            model_path = "lid.176.bin"
            wget.download(url, model_path)
        """ load fast-text model for lang id filt"""
        if os.path.exists(model_path):
            model = fasttext.load_model(model_path)
            print("Load fast-text model success.")
            return model
        else:
            return None

def delete_punc(line):
    punc="\"\',\.:!\?;-"
    punc=list(punc)
    for p in punc:
        line = line.strip(p)
    return line

def filter(lines,stop_words,lower_case=True):
    res_src,res_tgt,res_freq= [],[],[]
    src_set=set()
    tgt_set=set()
    # 消歧、去停用词
    for line in lines:
        line=line.strip()
        src,tgt,freq =line.split("\t")
        src, tgt = delete_punc(src), delete_punc(tgt)

        if (src not in src_set) and (tgt not in tgt_set): # 去重
            src_set.add(src)
            tgt_set.add(tgt)
            # 去除停用词
            if stop_words.is_word_valid(src,lang=src_lang) and stop_words.is_word_valid(tgt,lang=tgt_lang):
                res_src.append(src)
                res_tgt.append(tgt)
                res_freq.append(freq)
    # lang id 过滤
    src_langs = stop_words.get_lang_ids(word_list=res_src)
    tgt_langs = stop_words.get_lang_ids(word_list=res_tgt)
    res=[]
    print(len(src_langs),len(tgt_langs),len(res_src))
    for i in range(len(res_src)):
        if (src_langs[i]==stop_words.src_lang) and (tgt_langs[i]==stop_words.tgt_lang):
            if lower_case:
                res.append(f"{res_src[i].lower()}\t{res_tgt[i].lower()}\t{res_freq[i]}\n")
            else:
                res.append(f"{res_src[i]}\t{res_tgt[i]}\t{res_freq[i]}\n")

    print(f"Final dict length: {len(res)}")
    return res

if __name__ == '__main__':
    assert len(sys.argv) >= 5, f"usage: python {sys.argv[0]}  <src_lang> <tgt_lang> <in_file> <out_file> " \
                               f"<src_stop_file>(optional) <tgt_stop_file>(optional) <model_path>(optional)"

    src_lang=sys.argv[1]
    tgt_lang=sys.argv[2]
    in_file=sys.argv[3]
    out_file=sys.argv[4]
    src_stop=sys.argv[5] if len(sys.argv)>5 else None
    tgt_stop=sys.argv[6] if len(sys.argv)>6 else None
    model_path=sys.argv[7] if len(sys.argv)>7 else None

    lines=read_file(in_file)
    # build stopwords obj
    stop_words=StopWords(src_lang,tgt_lang,model_path)
    stop_words.load_words(src_lang,file_path=src_stop)
    stop_words.load_words(tgt_lang,file_path=tgt_stop)

    # filter out dict
    res=filter(lines,stop_words=stop_words)
    write_file(res,file=out_file)

