'''
input:  a-c.txt b-c.txt
output: a-b.txt
增加功能： fasttext过滤lang
'''
import os
import sys
import zhconv
from collections import OrderedDict
def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def get_landids(file):
    name = os.path.basename(file)
    src,tgt = name.replace(".txt","").split("-")
    return src,tgt

def filt_text(text,lang):
    if lang=="zh":
        text = zhconv.convert(text,"zh-cn")
    # fasttext
    return text

def build_dict(file_path):
    lines = read_file(file_path)
    src,tgt = get_landids(file_path)
    dic={"a2b":OrderedDict(),"b2a":OrderedDict()}
    for line in lines:
        line = line.strip()
        a,b = line.split()
        # zh process
        a = filt_text(a,lang=src)
        b = filt_text(b,lang=tgt)
        # skip error lang
        if a not in dic["a2b"].keys():
            dic["a2b"][a]=b
        if a not in dic["b2a"].keys():
            dic["b2a"][b]=a
    return dic

def pivot_dict(dic_a,dic_b):
    # dic_a = build_dict(file_a)  # ac ca
    # dic_b = build_dict(file_b)  # bc cb

    dic_ab = OrderedDict()
    for a, c in dic_a["a2b"].items():
        if a not in dic_ab.keys():
            # find b with c
            b = dic_b["b2a"].get(c, None)
            if b is None: continue
            dic_ab[a] = b
    return dic_ab

if __name__ == '__main__':
    assert len(sys.argv)==3, f"usage: python {sys.argv[0]} <file_a> <file_b>. "
    file_a = sys.argv[1]
    file_b = sys.argv[2]

    dic_a = build_dict(file_a) # ac ca
    dic_b = build_dict(file_b) # bc cb
    dic_ab = pivot_dict(dic_a,dic_b)

    a= get_landids(file_a)[0]
    b = get_landids(file_b)[0]

    dirname = os.path.dirname(file_a)
    out_file = os.path.join(dirname if dirname!="" else "./",f"{a}-{b}.txt" )

    res=[]
    for k,v in dic_ab.items():
        res.append(f"{k} {v}\n")
    write_file(res,out_file)