import sys
import os
import numpy as np
from tqdm import tqdm
def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def read_text_pair(src_file,tgt_file):
    res=[]
    with open(src_file,'r',encoding='utf-8') as fs,open(tgt_file,'r',encoding='utf-8') as ft:
        for line1,line2 in zip(fs.readlines(),ft.readlines()):
            line1=line1.strip()
            line2=line2.strip()
            res.append([line1,line2])
    return res

def upsample_data(res,final_len,seed=1):
    if final_len>len(res):
        # 从res中继续采样
        tmp=[]
        np.random.seed(seed=seed)
        idxs=np.random.randint(0,len(res),final_len-len(res))
        for idx in idxs:
            tmp.append(res[idx])
        res.extend(tmp)

    src_data=[data[0]+"\n" for data in res]
    tgt_data=[data[1]+"\n" for data in res]
    return src_data,tgt_data

if __name__ == '__main__':
    # params
    assert len(sys.argv)==6,f"usage: python {sys.argv[0]} <src-lang> <tgt-lang> <inprefix> <outfolder> <upsample len>"
    src_lang=sys.argv[1]
    tgt_lang=sys.argv[2]
    data_prefix=sys.argv[3]
    out_folder=sys.argv[4]
    final_len=float(sys.argv[5])
    # file
    src_file=f"{data_prefix}.{src_lang}"
    tgt_file=f"{data_prefix}.{tgt_lang}"
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    # split
    res=read_text_pair(src_file=src_file,tgt_file=tgt_file)
    src_data,tgt_data=upsample_data(res,final_len=int(final_len))
    # write
    write_file(res=src_data,file=os.path.join(out_folder,f"upsample.{src_lang}"))
    write_file(res=tgt_data,file=os.path.join(out_folder,f"upsample.{tgt_lang}"))
