'''
输入：1.单语文本  2.对应ngram
输出：{"text","score"}
'''
import kenlm
import json
import sys
from tqdm import tqdm
import pandas as pd
def score_fn(text,model):
    score = model.score(text, bos=False, eos=False)
    return score

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines= f.readlines()
    return lines

def write_json(res,file):
    with open(file,'w',encoding='utf-8') as f:
        json.dump(res,f,ensure_ascii=False)
    print(f'write to {file} success, total {len(res)} lines.')

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')


def get_score(lines,model):
    idx_ls = []
    score_ls = []
    for idx,line in tqdm(enumerate(lines)):
        score = score_fn(line.strip(),model)
        idx_ls.append(f"{idx}")
        score_ls.append(f"{score:.3f}")
    res={"idx":idx_ls,"score":score_ls}
    return res

def filt_by_score(js_data,ascending=True,topk=1000):
    df = pd.DataFrame.from_records(js_data)
    df["score"]=df["score"].astype("float")
    rn_indexs = df["score"].sort_values(ascending=ascending).index[:topk].tolist()
    rn_indexs = [f"{idx}\n" for idx in rn_indexs]
    return rn_indexs

if __name__ == '__main__':
    assert len(sys.argv)>=5,f"usage: python {sys.argv[0]} <infile> <outprefix> <nsample> <ngram_path> <ascending=True>(0/1)(optional)"
    infile = sys.argv[1]
    outprefix= sys.argv[2]
    nsample = int(sys.argv[3])
    ngram_path =sys.argv[4]
    ascending = True
    if len(sys.argv)==6:
        ascending = bool(int(sys.argv[5]))

    model = kenlm.Model(ngram_path)
    lines = read_file(infile)
    res = get_score(lines,model)
    rn_indexs = filt_by_score(res,ascending=ascending,topk=nsample)

    write_json(res,f"{outprefix}.json")
    write_file(rn_indexs,f"{outprefix}.idx")