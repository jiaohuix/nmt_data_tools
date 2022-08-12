#!/usr/bin/python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import fileinput
import hashlib
import sys
from tqdm import tqdm
from multiprocessing import Pool


def get_hashes_and_pairs(sent_pair):
    src,tgt= sent_pair
    text= f"{src.strip()}\t{tgt.strip()}"
    hash = hashlib.md5(text.encode()).hexdigest()
    return hash, sent_pair


def main(in_prefix,src_lang,tgt_lang,workers=1):
    src_in_file,tgt_in_file = f"{in_prefix}.{src_lang}",f"{in_prefix}.{tgt_lang}"
    src_out_file,tgt_out_file = f"{in_prefix}.dedup.{src_lang}",f"{in_prefix}.dedup.{tgt_lang}"

    seen = set()
    with open(src_in_file,"r",encoding="utf-8") as fr_src,open(tgt_in_file,"r",encoding="utf-8") as fr_tgt, \
        open(src_out_file, "w", encoding="utf-8") as fw_src, open(tgt_out_file, "w", encoding="utf-8") as fw_tgt:
        pool = Pool(processes=workers)
        paris=zip(fr_src,fr_tgt)
        results=pool.imap_unordered(get_hashes_and_pairs,paris,chunksize=1000)
        for i,(hash,sent_pairs) in tqdm(enumerate(results)):
            if hash not in seen:
                seen.add(hash)
                src_line,tgt_line = sent_pairs
                fw_src.write(src_line)
                fw_tgt.write(tgt_line)
        print(f"Deduplicate done! Total [{len(seen)}/{i+1}] lines.")

if __name__ == "__main__":
    assert len(sys.argv)==5,f"usage: python {sys.argv[0]} <in_prefix> <src_lang> <tgt_lang>  <workers>" \
                            f"\n write to out_prefix.dedup.lang  ."
    in_prefix=sys.argv[1]
    src_lang=sys.argv[2]
    tgt_lang=sys.argv[3]
    workers=int(sys.argv[4])

    main(in_prefix,src_lang,tgt_lang,workers=workers)
