'''
merge json dict
python merge_json.py  a.json.0 a.json.1 a.json.2 -> a.json
'''

#coding=utf-8
import os
import sys
import json
import numpy
from collections import OrderedDict

def read_json(file):
    with open(file,'r',encoding='utf-8') as f:
        data=json.load(f)
    return data

def write_json(worddict,file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(worddict, f, indent=2, ensure_ascii=False) # 这里indent是缩进的意思一般写为4 或者2
    print(f"write to file {file} success.")

def main():
    js_ls = []
    for filename in sys.argv[1:]:
        js_ls.append(read_json(filename))

    js_len = len(js_ls)
    res_dict = js_ls[0]
    max_count = 0
    for word, count in res_dict.items():
        # merge all count
        other_count = 0
        if js_len>1:
            other_count = sum([js_dic.get(word,0) for js_dic in js_ls[1:]])
        res_dict[word] = count + other_count
        # del other dict
        if js_len>1:
            for js_dic in js_ls[1:]:
                if word in js_dic:
                    del js_dic[word]
        # update max count
        if res_dict[word] > max_count:
            max_count = res_dict[word]

    # merge remaining dict
    if js_len>1:
        for js_dic in js_ls[1:]:
            for word,count in js_dic.items():
                res_dict[word] = count

                # update max count
                if res_dict[word] > max_count:
                    max_count = res_dict[word]

    # update speacial tokens' count
    res_dict['<s>'] = max_count + 10
    res_dict['<pad>'] = max_count + 9
    res_dict['</s>'] = max_count + 8
    res_dict['<unk>'] = max_count + 7

    # sort dict
    worddict = OrderedDict()
    res_dict = sorted(res_dict.items(), key=lambda x:x[1],reverse=True)
    for word, count in res_dict:
        worddict[word] = count

    # write json
    filename = sys.argv[1]
    root = os.path.dirname(filename)
    file = os.path.basename(filename)
    file = [char for char in file.split(".") if not char.isdigit() ]
    file = ".".join(file)
    filename = os.path.join(root,file)
    write_json(worddict,filename)


if __name__ == '__main__':
    main()
