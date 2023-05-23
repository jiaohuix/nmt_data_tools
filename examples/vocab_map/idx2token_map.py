import sys
import os
import json
import numpy as np
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

def write_json(worddict,file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(worddict, f, indent=2, ensure_ascii=False) # 这里indent是缩进的意思一般写为4 或者2
    print(f"write to file {file} success, total {len(worddict)} lines.")

def read_vocab_map(file):
    if not os.path.exists(file):
        return None
    with open(file,'r',encoding='utf-8') as f:
        data=json.load(f)
    vocab_map = {} # idx:[idxs...]
    for key, vals in data.items():
        vocab_map[int(key)] = [int(v) for v in vals]
    return vocab_map


def idx2token_map(idx_map,nmt_idx2token,bert_idx2token,bert_vocab):
  token_map = {}
  new_idx_map ={}
  new_token_map ={}
  for idx,sim_idxs in idx_map.items():
    token = nmt_idx2token[int(idx)]
    sim_tokens = [bert_idx2token[int(idx)] for idx in sim_idxs]
    token_map[token] = sim_tokens
    # 过滤
    if token in bert_vocab.keys():
        bert_idx = bert_vocab[token]
        new_idx_map[str(idx)] = [str(bert_idx)]
        new_token_map[token] = [token]
    else:
        new_idx_map[str(idx)] = sim_idxs
        new_token_map[token] = sim_tokens

  return token_map, new_idx_map, new_token_map


if __name__ == '__main__':
    assert len(sys.argv) == 4, f"usage: python {sys.argv[0]} <bert_dict> <nmt_dict> <idx_map_file>"
    bert_dict = sys.argv[1]
    nmt_dict = sys.argv[2]
    idx_map_file = sys.argv[3]

    bert_vocab, bert_idx2token = load_vocab(bert_dict)
    nmt_vocab, nmt_idx2token = load_vocab(nmt_dict)
    idx_map = read_vocab_map(idx_map_file)
    token_map, new_idx_map, new_token_map = idx2token_map(idx_map, nmt_idx2token, bert_idx2token,bert_vocab)
    write_json(token_map, "token_map.json")
    write_json(new_idx_map, "new_idx_map.json")
    write_json(new_token_map, "new_token_map.json")

