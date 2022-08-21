#coding=utf-8
from collections import OrderedDict
import fileinput
import sys

import numpy
import json


def main():
    for filename in sys.argv[1:]:
        print(filename)
        print('Processing', filename)
        word_freqs = OrderedDict()
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                words_in = line.strip().split(' ')
                for w in words_in:
                    w=w.strip()
                    if len(w)==0:continue
                    if w not in word_freqs:
                        word_freqs[w] = 0
                    word_freqs[w] += 1
        words = list(word_freqs.keys())
        freqs = list(word_freqs.values())

        sorted_idx = numpy.argsort(freqs)
        sorted_words = [words[ii] for ii in sorted_idx[::-1]]
        sorted_freqs = [freqs[ii] for ii in sorted_idx[::-1]]

        worddict = OrderedDict()

        worddict['<s>'] = sorted_freqs[0]+10
        worddict['<pad>'] = sorted_freqs[0]+9
        worddict['</s>'] = sorted_freqs[0]+8
        worddict['<unk>'] = sorted_freqs[0]+7
        # FIXME We shouldn't assume <EOS>, <GO>, and <UNK> aren't BPE subwords.
        for word,freq in zip(sorted_words,sorted_freqs):
            worddict[word] = freq

        # The JSON RFC requires that JSON text be represented using either
        # UTF-8, UTF-16, or UTF-32, with UTF-8 being recommended.
        # We use UTF-8 regardless of the user's locale settings.
        with open('%s.json'%filename, 'w', encoding='utf-8') as f:
            json.dump(worddict, f, indent=2, ensure_ascii=False)

        print('Done')

if __name__ == '__main__':
    main()
