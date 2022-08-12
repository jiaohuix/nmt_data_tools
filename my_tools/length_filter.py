'''
1.长度过滤
2.打印统计信息
3.去除bpe算长度
4.保留超过范围的数据
'''
import sys
import pandas as pd
from tqdm import tqdm
import argparse

def read_text_pair(src_file,tgt_file):
    res=[]
    with open(src_file,'r',encoding='utf-8') as fs,open(tgt_file,'r',encoding='utf-8') as ft:
        for line1,line2 in tqdm(zip(fs.readlines(),ft.readlines())):
            line1=line1.strip()
            line2=line2.strip()
            res.append([line1,line2])
    return res

def write_text_pair(text_pair_ls,out_src_file,out_tgt_file):
    src_pairs=[pair[0]+'\n' for pair in text_pair_ls]
    tgt_pairs=[pair[1]+'\n' for pair in text_pair_ls]
    write_file(src_pairs,out_src_file)
    write_file(tgt_pairs,out_tgt_file)

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.write(''.join(res))
    print(f'write to {file} success.')

def update_step_info(ratio=None,step_info={}):
    if ratio is None :
        step_info = {"1.5": 0, "2": 0, "2.5": 0, "3": 0}
    else:
        if ratio<=1.5: step_info["1.5"]+=1
        elif 1.5<ratio<2: step_info["2"]+=1
        elif 2.5<ratio<3: step_info["2.5"]+=1
        elif 3<ratio: step_info["3"]+=1
    return step_info

def length_filter(text_pair_ls,args):
    info={"ratio":[],"src_len":[],"tgt_len":[]}
    step_info=update_step_info()
    selected_pair, trash_pair=[], []
    for pair in text_pair_ls:
        linea,lineb=pair[0],pair[1]
        len_a,len_b=len(linea.split()),len(lineb.split())
        if args.remove_bpe:
            len_a=len(linea.replace("@@ ","").split())
            len_b=len(lineb.replace("@@ ","").split())

        max_len,min_len=max(len_a,len_b),min(len_a,len_b)
        ratio = max_len/min_len
        flag=True if (min_len>=args.low and max_len<=args.up) else False
        if flag and ratio > args.ratio: flag=False
        if flag:
            selected_pair.append(pair)
        else:
            trash_pair.append(pair)
        # static info
        info["ratio"].append(ratio)
        info["src_len"].append(len_a)
        info["tgt_len"].append(len_b)
        step_info=update_step_info(ratio,step_info)

    print(f'length filter | [{len(selected_pair)}/{len(text_pair_ls)}] samples retained, [{len(trash_pair)}/{len(text_pair_ls)}] were deleted.')

    df=pd.DataFrame(data=info)
    print(df.describe())
    print(f"step info: {step_info}")
    return selected_pair,trash_pair



if __name__ == '__main__':
    # low up ratio remove_bpe write_trash, print_info(1.5 2.5,3.5)
    print(f"usage: python {sys.argv[0]} --src-lang  --tgt-lang  --in-prefix  --out-prefix  --low 1 --up 200 --ratio 1.5 \n"
          f"--remove-bpe (optional) --wt (optional)")
    parser = argparse.ArgumentParser(description="Lang id filter")
    parser.add_argument('--src-lang',required=True,type=str,default='zh')
    parser.add_argument('--tgt-lang',required=True,type=str,default='en')
    parser.add_argument('--in-prefix',required=True,type=str,default=None)
    parser.add_argument('--out-prefix',required=True,type=str,default=None)
    parser.add_argument('--low',type=int,default=1)
    parser.add_argument('--up',type=int,default=175)
    parser.add_argument('--ratio',type=float,default=1.5)
    parser.add_argument('--remove-bpe',action="store_true",help="whether to remove bpe when compare length and ratio.")
    parser.add_argument('--wt',action="store_true",help="whether to write trash data pair, if true, write to [outprefix.trash.lang] .")

    args = parser.parse_args()

    src_file, tgt_file=f"{args.in_prefix}.{args.src_lang}",f"{args.in_prefix}.{args.tgt_lang}"
    out_src_file, out_tgt_file=f"{args.out_prefix}.{args.src_lang}",f"{args.out_prefix}.{args.tgt_lang}"
    pairs=read_text_pair(src_file,tgt_file)
    selected_pair,trash_pair=length_filter(pairs,args)

    write_text_pair(selected_pair,out_src_file=out_src_file,out_tgt_file=out_tgt_file)
    if args.wt: # write trash file
        out_src_file, out_tgt_file = f"{args.out_prefix}.trash.{args.src_lang}", f"{args.out_prefix}.trash.{args.tgt_lang}"
        write_text_pair(trash_pair, out_src_file=out_src_file, out_tgt_file=out_tgt_file)




