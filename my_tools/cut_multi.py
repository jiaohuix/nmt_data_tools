import os
import sys
import jieba
import zhconv
from tqdm import tqdm
from functools import partial
from multiprocessing import Pool
from pythainlp import word_tokenize

def cut_words(sent,lang="zh"):
    sent=sent.strip()
    if lang=="zh":
        sent=zhconv.convert(sent,"zh-cn")
        sent=" ".join(jieba.lcut(sent))
    elif lang=="th":
        sent=" ".join(word_tokenize(sent,keep_whitespace=False))
    sent+="\n"
    return sent

def main(infile,outfile,workers=1,lang="zh"):
    with open(infile,"r",encoding="utf-8") as fr,open(outfile,"w",encoding="utf-8") as fw:
        pool=Pool(processes=workers)
        cut_words_fn= partial(cut_words,lang=lang)
        sentences = pool.imap(cut_words_fn,fr,chunksize=1000)
        for sent in tqdm(sentences):
            fw.write(sent)

if __name__ == '__main__':
    assert len(sys.argv)==5,f"usage: python {sys.argv[0]} <infile> <outfile>  <workers> <lang>(zh/th) " \
                            f"\n Zh/Thai language multiprocess word cut."
    infile=sys.argv[1]
    outfile=sys.argv[2]
    workers=int(sys.argv[3])
    lang=sys.argv[4]
    assert lang in ["zh","th"]
    main(infile,outfile,workers,lang)