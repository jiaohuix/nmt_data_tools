#coding=utf-8
'''
输入多个文件，输出一个词表（json、vocab、dict）。多进程处理
'''
import sys
import json
import numpy
import argparse
import fileinput
from collections import OrderedDict
import multiprocessing
from functools import partial
from tqdm import tqdm

# def count_word_freq(sentence):
#     words = sentence.strip().split()
#     for word in words:
#         word = word.strip()
#         if len(word)==0: continue
#         word_freqs[word] = word_freqs.get(word,0) + 1
#     return sentence


# def count_word_freq(sentence,word_freqs):
#     words = sentence.strip().split()
#     for word in words:
#         word = word.strip()
#         if len(word)==0: continue
#         word_freqs[word] = word_freqs.get(word,0) + 1
#     return sentence

def count_word_freq(sentence):
    word_freqs = dict()
    words = sentence.strip().split()
    for word in words:
        word = word.strip()
        if len(word)==0: continue
        word_freqs[word] = word_freqs.get(word,0) + 1
    return word_freqs


def get_sorted_vocab(word_freqs):
    words = list(word_freqs.keys())
    freqs = list(word_freqs.values())

    sorted_idx = numpy.argsort(freqs)
    sorted_words = [words[ii] for ii in sorted_idx[::-1]]
    sorted_freqs = [freqs[ii] for ii in sorted_idx[::-1]]

    worddict = OrderedDict()

    worddict['<s>'] = sorted_freqs[0] + 10
    worddict['<pad>'] = sorted_freqs[0] + 9
    worddict['</s>'] = sorted_freqs[0] + 8
    worddict['<unk>'] = sorted_freqs[0] + 7
    # FIXME We shouldn't assume <s>, <pad>,</s>, and <unk> aren't BPE subwords.
    for word, freq in zip(sorted_words, sorted_freqs):
        worddict[word] = freq
    return worddict

def write_json(worddict,outfile):
    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(worddict, f, indent=2, ensure_ascii=False)
    print(f"Write to {outfile} success, total {len(worddict)} lines.")

def main():
    # python build_dictionary_parallel.py --outfolder out --lang zh --workers 4  train.zh mono.zh......
    parser = argparse.ArgumentParser()
    parser.add_argument("--outfolder", type=str, default="")
    parser.add_argument("--lang", type=str, default="")
    parser.add_argument("--min-freq", type=int, default=0)
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("files", nargs="*", help="input files")
    args = parser.parse_args()

    # global word_freqs
    word_freqs = OrderedDict()
    with fileinput.input(files=args.files,mode="r") as fr:
        # count_word_freq_fn = partial(count_word_freq,word_freqs=word_freqs)

        pool = multiprocessing.Pool(processes=args.workers)
        # count word frequence in parallel
        results = pool.imap_unordered(count_word_freq,fr,chunksize=1000) # word_freqs list
        # merge all word freq
        for word_freq in tqdm(results):
            for word,freq in word_freq.items():
                word_freqs[word] = word_freqs.get(word,0) + freq
        print(word_freqs)

    # sort word by reverse frequence order
    worddict = get_sorted_vocab(word_freqs)

    # write file
    outfile = f"{args.outfolder}.{args.lang}.json"
    write_json(worddict,outfile=outfile)


if __name__ == '__main__':

    main()
