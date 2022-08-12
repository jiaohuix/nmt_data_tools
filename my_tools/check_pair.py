'''
功能：检查长度信息，
与length_filter区别：
    1.length_filter必须写入范围内，可选范围外； check_pair只能可选写入范围外。
    2.check 非bpe语料对， 用于token后，bpe前
'''
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

def update_step_info(ratio=None,step_info={}):
    if ratio is None :
        step_info = {"1.5": 0, "2": 0, "2.5": 0, "3": 0}
    else:
        if ratio<=1.5: step_info["1.5"]+=1
        elif 1.5<ratio<2: step_info["2"]+=1
        elif 2.5<ratio<3: step_info["2.5"]+=1
        elif 3<ratio: step_info["3"]+=1
    return step_info


def check(srclines,tgtlines,upper=175,ratio=1.5):
    info={"ratio":[],"src_len":[],"tgt_len":[]}
    step_info=update_step_info()
    num_out_up,num_out_ratio=0,0
    for src,tgt in tqdm(zip(srclines,tgtlines)):
        src_words,tgt_words =src.strip().split(),tgt.strip().split()
        a,b=len(src_words),len(tgt_words)
        r= max(a,b)/min(a,b)
        if max(a,b)>upper: num_out_up+=1
        if r>ratio: num_out_ratio+=1

        # static info
        info["ratio"].append(r)
        info["src_len"].append(a)
        info["tgt_len"].append(b)
        step_info=update_step_info(ratio,step_info)

    df=pd.DataFrame(data=info)
    print(df.describe())
    print(f"{num_out_up} lines len > {upper}, {num_out_ratio} lines ratio > {ratio}.")
    print(f"step info: {step_info}")

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
        srcfile_out = f"{inprefix}.trash.{src_lang}"
        tgtfile_out = f"{inprefix}.trash.{tgt_lang}"
        write_file(res_src,srcfile_out)
        write_file(res_tgt,tgtfile_out)