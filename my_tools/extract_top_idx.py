import json
import os
import sys
from tqdm import tqdm
import pandas as pd

def read_json(file):
    with open(file,'r',encoding='utf-8') as f:
        js_data = json.load(f)
    return js_data

def write_json(res,file):
    with open(file,'w',encoding='utf-8') as f:
        json.dump(res,f,ensure_ascii=False)
    print(f'write to {file} success, total {len(res)} lines.')

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')


def filt_by_score(js_data,ascending=True,topk=1000):
    df = pd.DataFrame.from_records(js_data)
    df["score"]=df["score"].astype("float")
    sorted_df = df["score"].sort_values(ascending=ascending)
    print(sorted_df)
    rn_indexs = sorted_df.index[:topk].tolist()
    rn_indexs = [f"{idx}\n" for idx in rn_indexs]
    return rn_indexs

if __name__ == '__main__':
    assert len(sys.argv)>=4,f"usage: python {sys.argv[0]} <jsfile> <outprefix> <nsample> <ascending=True>(0/1)(optional)"
    jsfile = sys.argv[1]
    outprefix= sys.argv[2]
    nsample = int(sys.argv[3])
    ascending = True
    if len(sys.argv)==5:
        ascending = bool(int(sys.argv[4]))


    js_data = read_json(jsfile)
    rn_indexs = filt_by_score(js_data,ascending=ascending,topk=nsample)
    write_file(rn_indexs, os.path.join(os.path.dirname(jsfile),f"{outprefix}.idx"))
