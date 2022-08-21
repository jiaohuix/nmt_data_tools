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

def shuffle(res,dev_len,seed=1):
    ''' dev_len 若[0,1]则按比例取，若>1则按条数取'''
    assert dev_len>0 ,"dev set ratio should lager than 0."
    # shuffle
    shuffled_res=[]
    shuffle_idx=np.random.RandomState(seed=seed).permutation(np.arange(0,len(res))).tolist()
    for idx in tqdm(shuffle_idx):
        shuffled_res.append(res[idx])
    # dev len
    dev_len=int(dev_len) if dev_len>=1 else int(len(res)*dev_len)
    # split
    train_set=shuffled_res[:-dev_len]
    dev_set=shuffled_res[-dev_len:]
    return train_set,dev_set

if __name__ == '__main__':
    # params
    assert len(sys.argv)==6,f"usage: python {sys.argv[0]} <src-lang> <tgt-lang> <inprefix> <outfolder> <dev len>"
    src_lang=sys.argv[1]
    tgt_lang=sys.argv[2]
    data_prefix=sys.argv[3]
    out_folder=sys.argv[4]
    dev_len=float(sys.argv[5])
    # file
    src_file=f"{data_prefix}.{src_lang}"
    tgt_file=f"{data_prefix}.{tgt_lang}"
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    # split
    res=read_text_pair(src_file=src_file,tgt_file=tgt_file)
    train_set,dev_set=shuffle(res,dev_len=dev_len)
    # write
    write_file(res=[data[0]+"\n" for data in train_set],file=os.path.join(out_folder,f"train.{src_lang}"))
    write_file(res=[data[1]+"\n" for data in train_set],file=os.path.join(out_folder,f"train.{tgt_lang}"))
    write_file(res=[data[0]+"\n" for data in dev_set],file=os.path.join(out_folder,f"dev.{src_lang}"))
    write_file(res=[data[1]+"\n" for data in dev_set],file=os.path.join(out_folder,f"dev.{tgt_lang}"))