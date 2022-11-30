''' postprocess for wechat WMT22 paper: Summer: WeChat Neural Machine Translation Systems for the WMT22 Biomedical Translation Task'''
import os
import sys
import jieba
import zhconv
from tqdm import tqdm
from functools import partial
from multiprocessing import Pool

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def process_uppercase(words):
    ''' wechat WMT22 paper: Summer: WeChat Neural Machine Translation Systems for the WMT22 Biomedical Translation Task'''
    res = []
    for word in words:
        if word.isupper():
            res.extend(["_UU_",word.lower()])
        elif word[0].isupper():
            res.extend(["_U_",word[0].upper()+ word[1:]])
        else:
            res.append(word)
    return res

def recover_uppercase(words):
    res = []
    ptr = 0
    while ptr < (len(words) - 1) :
        word = words[ptr]
        next_word = words[ptr+1]
        if word == "_UU_":
            res.append(next_word.upper())
            ptr += 2
        elif word == "_U_":
            next_word =  next_word[0].upper()+ next_word[1:]
            res.append(next_word)
            ptr += 2
        else:
            res.append(word)
            ptr += 1

    if res[-1].lower() != words[-1].lower():
        res.append(words[-1])

    return res

def cut_words(sent,lang="zh"):
    sent=sent.strip()
    if lang=="zh":
        sent=zhconv.convert(sent,"zh-cn")
        words = jieba.lcut(sent)
    elif lang=="th":
        from pythainlp import word_tokenize
        words = word_tokenize(sent,keep_whitespace=False)
    else:
        from sacremoses import MosesTokenizer
        tokenizer = MosesTokenizer(lang=lang)
        words = tokenizer.tokenize(sent)
        words = process_uppercase(words)
    sent = " ".join(words) + "\n"
    return sent

def main(infile,outfile,lang="en"):
    lines = read_file(infile)
    res = []
    from sacremoses import  MosesDetokenizer
    detok = MosesDetokenizer(lang)
    for line in lines:
        words = line.strip().split()
        words = recover_uppercase(words)
        sent = detok.detokenize(words)
        res.append(sent + "\n")
    write_file(res,outfile)




if __name__ == '__main__':
    assert len(sys.argv)==4,f"usage: python {sys.argv[0]} <infile> <outfile> <lang>" \
                            f"\n Zh/Thai language multiprocess word cut."
    infile=sys.argv[1]
    outfile=sys.argv[2]
    lang=sys.argv[3]
    main(infile,outfile,lang)
