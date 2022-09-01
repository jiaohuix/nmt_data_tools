import sys
import os
import numpy as np
from tqdm import tqdm

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def shuffle(lines,seed=1):
    ''' dev_len 若[0,1]则按比例取，若>1则按条数取'''
    # shuffle
    shuffled_res=[]
    shuffle_idx=np.random.RandomState(seed=seed).permutation(np.arange(0,len(lines))).tolist()
    for idx in tqdm(shuffle_idx):
        shuffled_res.append(lines[idx])
    return shuffled_res

if __name__ == '__main__':
    assert len(sys.argv)==4,f"usage: python {sys.argv[0]} <lang>  <data_prefix> <out_folder>"
    # params
    lang=sys.argv[1]
    data_prefix=sys.argv[2]
    out_folder=sys.argv[3]
    # file
    file=f"{data_prefix}.{lang}"
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    # split
    lines = read_file(file)
    lines=shuffle(lines)
    # write
    write_file(res=lines,file=os.path.join(out_folder,f"shuffle.{lang}"))

