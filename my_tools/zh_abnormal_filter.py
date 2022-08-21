import sys
import pandas as pd
from tqdm import tqdm
import numpy as np
import argparse

def read_text_pair(src_file,tgt_file):
    with open(src_file,'r',encoding='utf-8') as fs,open(tgt_file,'r',encoding='utf-8') as ft:
        lines1,lines2 = fs.readlines(),ft.readlines()
        
    return lines1,lines2

def write_text_pair(text_pair_ls,out_src_file,out_tgt_file):
    src_pairs=[pair[0] for pair in text_pair_ls]
    tgt_pairs=[pair[1] for pair in text_pair_ls]
    write_file(src_pairs,out_src_file)
    write_file(tgt_pairs,out_tgt_file)

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines


def is_all_japanese(strs):
    for _char in strs:
        if not '\u0800' <= _char <= '\u4e00':
            return False
    return True

def get_words_count(lines):
    words_count = {}
    for line in lines:
        words = line.strip().split()
        for word in words:
            words_count[word] = words_count.get(word,0)+1
    return words_count


def get_dict(words_count,min_freq=20):
    normal_dict={}
    abnormal_dict={}
    for k,v in words_count.items():
        if is_all_japanese(k) and v<min_freq:
            # print(k,v)
            abnormal_dict[k]=v
        else:
            normal_dict[k]=v
    return normal_dict,abnormal_dict


def get_abnormal_lines_id_score(lines_zh,normal_dict,abnormal_dict):
    '''
        找到包含异常词的id，并计算他们分数score，留给下一个函数处理；score>threshold, line_zh[id]="",line_other[id]="";
        score<threshold, 则line_zh[id]过一个过滤器，过滤掉规则内的异常词。
    '''
    ids=[]
    scores=[]
    score_fn = lambda freq: 0 if freq > 100 else (100 - freq) / 100
    # res=[]
    for idx,line in enumerate(lines_zh):
        flag = False
        # tmp = ""
        sent_score=[] # freq>100, s=0; freq<100, s=(100-freq)/100
        for word in line.strip().split():
            if word in abnormal_dict.keys():
                # tmp+=f"[{word}] "
                flag=True
                freq=abnormal_dict[word]
                sent_score.append(score_fn(freq))
            else:
                # tmp+= f"{word} "
                freq=normal_dict[word]
                sent_score.append(score_fn(freq))

        if flag:
            avg_score= sum(sent_score)/len(sent_score)
            ids.append(idx)
            scores.append(avg_score)
            # res.append(f"score={avg_score:.3f}\t{tmp}")
    return ids, scores

def zh_text_filter(text):
    """ filter zh sentence by rule. """
    drop_cahrs="╭╰ㄤ㖊㖞ㄅㄆㄇ″ㄎレテョにむㄢグイキㄇぃㄥゾなカバヺのいงซあミんㇳヌノメㇸㇿヸホฮヒがパえツ〜ぬㄨらくビピヵースザッよヅフヿマねไサㇵㄛわリต※ダㄅ์コれㄎゥィュินジㇴㄉⅤまืゴやケワㇾㄠポㇺ้ギะブㇶち╩㈱モとェヲおベトタはさ゠しヨウルㇹヤゅ㓥รุオㄞアヰคニもัㇱかพをズムゲยヽすぐอヹจへㇽラシสㇻつロวみㄐペㇰプォ่ㄩゼ∕ガヂเヶมひทㄙドばㄓ・ャㄖㄌハそエセネユㇼソีㄒぎるクりてヾヘㄘデボゆふめナㇷチけせ㎡ろา┕ㄈヮンヱきほうこどヷたヴㄆァㄗㇲ"
    char_map= { '⼈':'人',  'ㄚ':'丫', '⻔':'门', '⼝':'口', '⼦':'子'
     ,  '⾕':'谷', '⾯':'面', '∣':'1', '⾃':'自', '⾮':'非', '⼩':'小', '⽤':'用', '⽽':'而', '⼴':'广', '⼊':'入',
     '⼼':'心', '⼯':'共', '⾛':'走', '⽣':'生', '⽿':'耳', '⽶':'米', '⻄':'西', '⽬':'目', '⽂':'文', '═':'=', '⽞':'玄', '⼜':'又', '⾜':'足',
       '⻅':'见', '⾄':'至', '⼤':'大','⾸':'首', '⺟':'母', '⾏':'行', '⽉':'月', '⽴':'立','冇':'有'}
    words=text.strip().split()
    res=[]
    for word in words:
        if word in drop_cahrs:continue
        elif word in char_map:
            res.append(char_map[word])
        else:
            res.append(word)
    text = " ".join(res)+"\n"
    return text

def update_pair_by_id_score(lines_zh,lines_other,ids,scores,threshold=0.45):

    trash_update = [] # score<threshold
    trash_drop = [] # score>=threshold
    for idx in range(len(ids)):
        abnormal_zh_idx = ids[idx]
        score = scores[idx]
        if score>=threshold:
            trash_drop.append(f"Score: [{score:.3f}], Sentence: [{lines_zh[abnormal_zh_idx]}]")

            lines_zh[abnormal_zh_idx]=""
            lines_other[abnormal_zh_idx]=""
        else:
            lines_zh[abnormal_zh_idx] = zh_text_filter(lines_zh[abnormal_zh_idx])
            trash_update.append(f"Score: [{score:.3f}], Sentence: [{lines_zh[abnormal_zh_idx]}]")
    return lines_zh,lines_other,trash_update, trash_drop


def print_ls(res):
    print("*"*50)
    for i,line in enumerate(res):
        print(i,line)
    print(f" Total {i+1} lines.")
    print("*"*50)

if __name__ == '__main__':
    # python my_tools/zh_abnormal_filter.py --zh-lang zh --other-lang th --in-prefix data_zhth/train.tok --out-prefix data_zhth/train.deab --threshold 0.45 --min-freq 20 --pt
    print(f"usage: python {sys.argv[0]} --zh-lang zh --other-lang th --in-prefix  --out-prefix  --threshold 0.45 --min-freq 20 --wt(optional)")
    parser = argparse.ArgumentParser(description="Lang id filter")
    parser.add_argument('--zh-lang',required=True,type=str,default='zh')
    parser.add_argument('--other-lang',required=True,type=str,default='en')
    parser.add_argument('--in-prefix',required=True,type=str,default=None)
    parser.add_argument('--out-prefix',required=True,type=str,default=None)
    parser.add_argument('--threshold',type=float,default=0.45,help="sentence score > threshold will be seen as anomaly.")
    parser.add_argument('--min-freq',type=int,default=20,help="if word freq < min_freq , it has a chance of being an anomaly,")
    parser.add_argument('--wt',action="store_true",help="whether to write trash data pair")

    args = parser.parse_args()

    zh_file, other_file=f"{args.in_prefix}.{args.zh_lang}",f"{args.in_prefix}.{args.other_lang}"
    out_zh_file, out_other_file=f"{args.out_prefix}.{args.zh_lang}",f"{args.out_prefix}.{args.other_lang}"
    lines_zh,lines_other=read_text_pair(zh_file,other_file)

    words_count_zh=get_words_count(lines_zh)
    normal_dict,abnormal_dict = get_dict(words_count_zh,min_freq=args.min_freq)

    ids, scores = get_abnormal_lines_id_score(lines_zh,normal_dict,abnormal_dict)

    new_lines_zh, new_lines_other , trash_update, trash_drop= update_pair_by_id_score(lines_zh,lines_other,ids,scores, threshold=args.threshold)

    len_raw = len(lines_zh)
    len_new = len_raw-len(ids)
    print(f"Zh abnormal filter: [{len_new}/{len_raw}]")

    selected_pair = list(zip(new_lines_zh,new_lines_other))
    write_text_pair(selected_pair,out_src_file=out_zh_file,out_tgt_file=out_other_file)
    if args.wt: # write trash file
        out_zh_file_update = f"{args.out_prefix}.update.{args.zh_lang}"
        out_zh_file_drop = f"{args.out_prefix}.trash.{args.zh_lang}"
        write_file(trash_update,out_zh_file_update)
        write_file(trash_drop,out_zh_file_drop)



