import os
import sys
import json

def read_json(file):
    with open(file,'r',encoding='utf-8') as f:
        data=json.load(f)
    return data

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def json2dict(js_data,min_freq):
    keys = list(js_data.keys())[4:]
    freqs = list(js_data.values())[4:]
    res = [f"{key} {freq}\n" for key, freq in zip(keys, freqs) if freq > min_freq]
    return res


if __name__ == '__main__':
    assert len(sys.argv)>=3,f"usage: python {sys.argv[0]} <infile> <outfile> <min_freq>(optional)"
    infile=sys.argv[1]
    outfile=sys.argv[2]
    min_freq = 0
    if len(sys.argv)>3:
        min_freq = int(sys.argv[3])

    js_data=read_json(infile)
    res=json2dict(js_data,min_freq)
    write_file(res,outfile)