import os
import sys
import time
import logging
from tqdm import tqdm
logger=logging.getLogger('cut')
logger.setLevel(logging.DEBUG)

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')


def cut(sent, backend="jieba"):
    if backend=="jieba":
        import zhconv
        import jieba
        sent = zhconv.convert(sent, "zh-cn")
        sent = " ".join(jieba.lcut(sent))
    elif backend=="thulac":
        import thulac
        thu1 = thulac.thulac(seg_only=True,T2S=True)
        sent = thu1.cut(sent, text=True)
    elif backend=="ltp":
        pass
    return sent

def process(lines,backend="jieba"):
    res = []
    for sent in tqdm(lines):
        sent=sent.strip()
        sent = cut(sent,backend=backend) +'\n'
        res.append(sent)
    return res

if __name__ == '__main__':
    assert len(sys.argv)>=3,f"usage: python {sys.argv[0]} <infile> <outfile> <backend>"
    infile=sys.argv[1]
    outfile=sys.argv[2]
    backend=sys.argv[3] if len(sys.argv)==4 else "jieba"
    assert backend in ["jieba", "thulac", "ltp"]
    print(f"segment backend: {backend}.")

    lines=read_file(infile)
    res = process(lines, backend=backend)
    write_file(res,outfile)
