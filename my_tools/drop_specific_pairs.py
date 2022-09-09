#!/usr/bin/python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
'''
给定两个语料对prefix1和prefix2，语言为lang1 lang2，
从prefix1.lang 中剔除 prefix2的所有数据
思路：用hashcode把prefix2的src和tgt拼接的语料转hash，放入set，若见过则删除。（prefix2逐个处理，prefix1并行删除）
1.参数
2.读取drop_prefix.lang，记录hash进集合seen
3.main里面去除seen里的
'''

import argparse
import fileinput
import hashlib
import sys
from tqdm import tqdm
from multiprocessing import Pool


def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines


def get_hashes_and_pairs(sent_pair):
    src,tgt= sent_pair
    text= f"{src.strip()}\t{tgt.strip()}"
    hash = hashlib.md5(text.encode()).hexdigest()
    return hash, sent_pair


def get_drop_hash(prefix,src_lang,tgt_lang):
    drop_hash= set()
    src_in_file,tgt_in_file = f"{prefix}.{src_lang}",f"{prefix}.{tgt_lang}"
    with open(src_in_file,"r",encoding="utf-8") as fr_src,open(tgt_in_file,"r",encoding="utf-8") as fr_tgt:
        for src,tgt in zip(fr_src.readlines(),fr_tgt.readlines()):
            hash,pair = get_hashes_and_pairs([src,tgt])
            if hash not in drop_hash:
                drop_hash.add(hash)
    print(f"Corpus pair to be deleted: [{len(drop_hash)}] pairs.")
    return drop_hash

def main(in_prefix,src_lang,tgt_lang,drop_hash,workers=1):
    src_in_file,tgt_in_file = f"{in_prefix}.{src_lang}",f"{in_prefix}.{tgt_lang}"
    src_out_file,tgt_out_file = f"{in_prefix}.drop.{src_lang}",f"{in_prefix}.drop.{tgt_lang}"
    num_res=0
    with open(src_in_file,"r",encoding="utf-8") as fr_src,open(tgt_in_file,"r",encoding="utf-8") as fr_tgt, \
        open(src_out_file, "w", encoding="utf-8") as fw_src, open(tgt_out_file, "w", encoding="utf-8") as fw_tgt:
        pool = Pool(processes=workers)
        paris=zip(fr_src,fr_tgt)
        results=pool.imap_unordered(get_hashes_and_pairs,paris,chunksize=1000)
        for i,(hash,sent_pairs) in tqdm(enumerate(results)):
            if hash not in drop_hash:
                # seen.add(hash)
                src_line,tgt_line = sent_pairs
                fw_src.write(src_line)
                fw_tgt.write(tgt_line)
                num_res+=1
        print(f"Delete the specified language is complete! Total [{num_res}/{i+1}] paris.")

if __name__ == "__main__":
    assert len(sys.argv)==6,f"usage: python {sys.argv[0]} <src_lang> <tgt_lang> <main_prefix> <drop_prefix>  <workers>" \
                            f"\n write to main_prefix.drop.lang  ."
    src_lang=sys.argv[1]
    tgt_lang=sys.argv[2]
    main_prefix=sys.argv[3]
    drop_prefix=sys.argv[4]
    workers=int(sys.argv[5])

    drop_hash = get_drop_hash(drop_prefix,src_lang,tgt_lang)

    main(main_prefix,src_lang,tgt_lang,drop_hash,workers=workers)
