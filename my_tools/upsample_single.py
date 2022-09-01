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

def upsample_data(lines,final_len,seed=1):
    if final_len>len(lines):
        # 从res中继续采样
        tmp=[]
        np.random.seed(seed=seed)
        idxs=np.random.randint(0,len(lines),final_len-len(lines))
        for idx in idxs:
            tmp.append(lines[idx])
        lines.extend(tmp)

    return lines

if __name__ == '__main__':
    # params
    assert len(sys.argv)==5,f"usage: python {sys.argv[0]} <lang>  <inprefix> <outfolder> <upsample len>"
    lang=sys.argv[1]
    data_prefix=sys.argv[2]
    out_folder=sys.argv[3]
    final_len=float(sys.argv[4])
    # file
    file=f"{data_prefix}.{lang}"
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    # split
    lines = read_file(file)
    lines=upsample_data(lines,final_len=int(final_len))
    # write
    write_file(res=lines,file=os.path.join(out_folder,f"upsample.{lang}"))
