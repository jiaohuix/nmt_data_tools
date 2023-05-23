import sys
import os
import json
import numpy as np
import fasttext

def load_vocab(file, remove_bpe=True):
    vocab = {}
    idx2token = {}
    with open(file, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f.readlines()):
            line = line.strip()
            if remove_bpe:
                line = line.replace("@@", "")
            vocab[line] = idx
            idx2token[idx] = line
    return vocab, idx2token


def encode_vector(vocab, model):
    res = []
    for token, idx in vocab.items():
        vec = model.get_word_vector(token)
        res.append(vec)

    return np.vstack(res)

if __name__ == '__main__':
    assert len(sys.argv) == 4, f"usage: python {sys.argv[0]} <model> <dict> <outfile(xx.bin)>"
    model = sys.argv[1]
    dict = sys.argv[2]
    outfile = sys.argv[3]
    model = fasttext.load_model(model)
    vocab, idx2token = load_vocab(dict)
    vecs = encode_vector(vocab, model)
    vecs.tofile(outfile)
    print(f"saved to {outfile} success.")