import os
import sys
import pandas as pd
from tqdm import tqdm
def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.write(''.join(res))
    print(f'write to {file} success.')

def check(srclines,tgtlines,upper=175,ratio=1.5):
    up_max=upper
    ratio_max=ratio
    num_max_u=0
    num_max_r=0

    ratios=[]
    src_len=[]
    tgt_len=[]
    res_src=[]
    res_tgt=[]
    for src,tgt in tqdm(zip(srclines,tgtlines)):
        src_words,tgt_words =src.strip().split(),tgt.strip().split()
        a,b=len(src_words),len(tgt_words)
        r= max(a,b)/min(a,b)
        ratios.append(r)
        if r>ratio_max:
            num_max_r+=1
            res_src.append(src)
            res_tgt.append(tgt)
        if max(a,b)>up_max: num_max_u+=1
        src_len.append(a)
        tgt_len.append(b)

    df=pd.DataFrame(data={"ratios":ratios,"src_len":src_len,"tgt_len":tgt_len})
    print(df.describe())
    print(f"{num_max_u} lines len > {up_max},{num_max_r} lines ratio > {ratio_max}.")
    return res_src,res_tgt

if __name__ == '__main__':
    assert len(sys.argv)>=6,f"usage: python {sys.argv[0]} <inprefix> <src_lang> <tgt_lang> <upper> <ratio> <write>(0/1, optional)"
    inprefix=sys.argv[1]
    src_lang=sys.argv[2]
    tgt_lang=sys.argv[3]
    upper=int(sys.argv[4])
    ratio=float(sys.argv[5])
    w=False
    if len(sys.argv)>6:
        w = bool(int(sys.argv[6]))

    srcfile=f"{inprefix}.{src_lang}"
    tgtfile=f"{inprefix}.{tgt_lang}"

    srclines=read_file(srcfile)
    tgtlines=read_file(tgtfile)
    res_src, res_tgt= check(srclines,tgtlines,upper,ratio)
    if w:
        srcfile_out = f"{inprefix}.check.{src_lang}"
        tgtfile_out = f"{inprefix}.check.{tgt_lang}"
        write_file(res_src,srcfile_out)
        write_file(res_tgt,tgtfile_out)