import sys
import numpy as np
from tqdm import tqdm

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def scorer(text,model):
    score = model.score(text, bos=False, eos=False)
    return round(score,3)

def processer(lines,model):
    res = []
    for line in tqdm(lines):
        line = line.strip()
        score = scorer(line,model)
        res.append(f"{score}\n")
    return res

if __name__ == '__main__':
    # 排序，默认小到大
    assert len(sys.argv)>=4,f"usage: python {sys.argv[0]} <infile> <outfile> <scorefile>  <reverse>(0/1)"
    infile = sys.argv[1]
    outfile = sys.argv[2]
    scorefile = sys.argv[3]
    rev = False
    if len(sys.argv)==5:
        rev = True if sys.argv[4] == "1" else False

    lines = read_file(infile)
    scores = [float(score.strip()) for score in read_file(scorefile)]
    scores = np.array(scores)
    if rev:
        scores = -1 * scores
    idxs = np.argsort(scores)
    res = []
    for idx in idxs:
        res.append( str(lines[idx]).strip()+"\n")
    write_file(res,outfile)
    if rev:
        scores = -1 * scores

    scores = [f"{round(score,3)}\n" for score in  scores[idxs].tolist()]
    write_file(scores,f"{outfile}.score")
