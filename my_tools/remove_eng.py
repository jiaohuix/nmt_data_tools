import re
import sys
from tqdm import tqdm
import argparse

def read_text_pair(src_file,tgt_file):
    print("Reading text pair...")
    with open(src_file,'r',encoding='utf-8') as fs,open(tgt_file,'r',encoding='utf-8') as ft:
        res = list(zip(fs.readlines(),ft.readlines()))
    return res

def is_all_chinese(strs):
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True

def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def delete_en_from_zh(sent,k=2):
    # tolerant for k words
    new_sent=""
    alpha_cont=0 # 超过2就要删除
    temp=""
    sent=sent.split()
    for word in sent:
        if is_contains_chinese(word):
            if alpha_cont<=k:
                new_sent+=temp # 把以前的加上
            temp=" "
            new_sent+=word
            alpha_cont=0 # 重新计数
        else: # 字母
            alpha_cont+=1
            temp+=word+" "
    return new_sent

def is_contains_en(word):
    my_re = re.compile(r'[A-Za-z]', re.S)
    res = re.findall(my_re, word)
    if len(res):
        return True
    else:
        return False

def delete_en_from_other(sent,lang="zh",k=2):
    if lang=="zh": return delete_en_from_zh(sent,k)
    # tolerant for k words
    new_sent=""
    alpha_cont=0 # 超过2就要删除
    temp=""
    sent=sent.split()
    for word in sent:
        if not is_contains_en(word):
            if alpha_cont<=k:
                new_sent+=temp # 把以前的加上
            temp=" "
            new_sent+=word
            alpha_cont=0 # 重新计数
        else: # 字母
            alpha_cont+=1
            temp+=word+" "
    return new_sent


def write_text_pair(text_pair_ls,out_src_file,out_tgt_file):
    src_pairs=[pair[0] for pair in text_pair_ls]
    tgt_pairs=[pair[1] for pair in text_pair_ls]
    write_file(src_pairs,out_src_file)
    write_file(tgt_pairs,out_tgt_file)

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def process(text_pair_ls,src_lang="zh",tgt_lang="ar",k=2):
    new_pair=[]
    for pair in tqdm(text_pair_ls):
        text_src, text_tgt = pair[0].strip().lower(), pair[1].strip().lower()
        text_src = delete_en_from_other(text_src,lang=src_lang,k=k)
        text_tgt = delete_en_from_other(text_tgt,lang=tgt_lang,k=k)
        new_pair.append((text_src+"\n",text_tgt+"\n"))
    return new_pair

if __name__ == '__main__':
    assert len(sys.argv)>=5,f"usage: python {sys.argv[0]} <src-lang> <tgt-lang>  <in-prefix > <out-prefix> <k words>(optional)"
    src_lang=sys.argv[1]
    tgt_lang=sys.argv[2]
    in_prefix=sys.argv[3]
    out_prefix=sys.argv[4]
    if len(sys.argv)>5:
        k=int(sys.argv[5])
    else:
        k=2
    src_file, tgt_file=f"{in_prefix}.{src_lang}",f"{in_prefix}.{tgt_lang}"
    out_src_file, out_tgt_file=f"{out_prefix}.{src_lang}",f"{out_prefix}.{tgt_lang}"
    pairs=read_text_pair(src_file,tgt_file)
    new_pair=process(pairs,
                                 src_lang=src_lang,
                                 tgt_lang=tgt_lang,
                                 k=k)
    write_text_pair(new_pair,out_src_file=out_src_file,out_tgt_file=out_tgt_file)
