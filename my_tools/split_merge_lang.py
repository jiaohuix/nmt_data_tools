'''
usage: 把混合语言的文件按照开头的language token进行分割或合并，便于对不同语言执行moses。
eg:
    split:
            train.de
                xxxxxx
            train.en
                yyyyy
            train.idx
                en,1
                de,1

    merge: train.src
            <de> xxxxxx
            <en> yyyyyy
        or (remove-lang):
            xxxxxx
            yyyyyy
python split_merge_lang.py --prefix dataset/iwslt14_de_en_mrasp_raw/valid --langs src --mode split
python split_merge_lang.py --prefix dataset/iwslt14_de_en_mrasp_raw/valid --langs de,en --mode merge --remove-lang

'''
import os
import sys
import argparse
from pprint import pprint

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.write(''.join(res))
    print(f'write to {file} success.')


def split_file(prefix,lang):
    # read
    in_file = f"{prefix}.{lang}"
    lines=read_file(in_file)
    # split
    res={"idx":[]} # "en":[] "de":[] "idx":["en,2","de,3"]
    for idx,line in enumerate(lines):
        line = line.strip()
        lang = line.split()[0].replace("<","").replace(">","")
        line = " ".join(line.split()[1:])
        if not lang in res.keys():
            res[lang]=[]
        res[lang].append(f"{line}\n")
        lang_idx = len(res[lang])-1
        res["idx"].append(f"{lang},{lang_idx}\n")

    # write
    idx = res["idx"]
    write_file(idx,file=f"{prefix}.idx")
    del res["idx"]
    for lang,ls in res.items():
        file_name = f"{prefix}.{lang}"
        write_file(ls,file=file_name)

    print("Split over.")

def merge_file(prefix,langs=[],remove_tmp=True,remove_lang=False):
    idx_file = f"{prefix}.idx"
    assert os.path.isfile(idx_file)
    idx_lines = read_file(idx_file)
    if remove_tmp:os.remove(idx_file)
    lang_dic={}
    res=[]
    for lang in langs:
        file_name=f"{prefix}.{lang}"
        assert os.path.isfile(file_name)
        lang_dic[lang]=read_file(file_name)
        if remove_tmp: os.remove(file_name)
    for idx_line in idx_lines:
        idx_line = idx_line.strip()
        lang,lang_idx = idx_line.split(",")
        lang_sentence = lang_dic[lang][int(lang_idx)]
        if not remove_lang:
            lang_sentence = f"<{lang}> "+lang_sentence
        res.append(lang_sentence)

    # write
    write_file(res,file=f"{prefix}.merge")
    print("Merge over.")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prefix', type=str, default="train", help="replace file, prefix.src/tgt ,default=train")
    parser.add_argument('--langs', type=str, help="split or merge file suffix, sep=',' ." )  # en-de.txt
    parser.add_argument('--mode', type=str, default="split", help="[split|merge]")
    parser.add_argument('--remove-lang', action="store_true",help="Whether to remove lang token prefix.")
    args = parser.parse_args()
    pprint(args)
    langs=args.langs.split(",")
    if args.mode=="split":
        suffix=langs[0]
        split_file(prefix=args.prefix,lang=suffix)
    elif args.mode=="merge":
        merge_file(prefix=args.prefix,langs=langs,remove_lang=args.remove_lang)
    else:
        print("mode error, mode shoud in [split|merge].")