import sys
import fasttext
from tqdm import tqdm
import argparse

def read_text_pair(src_file,tgt_file):
    print("Reading text pair...")
    with open(src_file,'r',encoding='utf-8') as fs,open(tgt_file,'r',encoding='utf-8') as ft:
        res = list(zip(fs.readlines(),ft.readlines()))
    return res


# def write_text_pair(text_pair_ls, out_src_file, out_tgt_file):
#     print("Writing text pair...")
#     src_pairs, tgt_pairs = list(zip(*text_pair_ls))
#     del text_pair_ls
#     write_file(src_pairs, out_src_file)
#     del src_pairs
#     write_file(tgt_pairs, out_tgt_file)
#     del tgt_pairs

def write_text_pair(text_pair_ls,out_src_file,out_tgt_file):
    src_pairs=[pair[0] for pair in text_pair_ls]
    tgt_pairs=[pair[1] for pair in text_pair_ls]
    write_file(src_pairs,out_src_file)
    write_file(tgt_pairs,out_tgt_file)

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def length_filter(text_pair_ls,low=1,up=200,ratio=1.5):
    new_pair=[]
    for pair in tqdm(text_pair_ls):
        linea,lineb=pair[0].split(),pair[1].split()
        len_a,len_b=len(linea),len(lineb)
        max_len,min_len=max(len_a,len_b),min(len_a,len_b)
        flag=True if (min_len>=low and max_len<=up) else False
        if flag and (max_len/min_len)>ratio:
            flag=False

        if flag:
            new_pair.append(pair)
    print(f'length filter | [{len(new_pair)}/{len(text_pair_ls)}] samples retained, [{len(text_pair_ls)-len(new_pair)}/{len(text_pair_ls)}] were deleted.')
    return new_pair

def lang_id_filter(text_pair_ls,model_path,src_lang='zh',tgt_lang='en',threshold=None,report_neg=False,remove_bpe=False):
    print("Lang id filtering...")
    model=fasttext.load_model(model_path)
    new_pair=[]
    trash_pair=[]
    for pair in tqdm(text_pair_ls):
        a, b = pair[0].strip().lower(), pair[1].strip().lower()
        if remove_bpe:
            a = a.replace("@@ ","")
            b = b.replace("@@ ","")

        labels,scores=model.predict([a,b])
        labels=[label[0].replace('__label__','') for label in labels]
        scores=[float(score) for score in scores]
        # src和tgt标签都要正确
        flag=True if all((labels[0]==src_lang,labels[1]==tgt_lang)) else False
        # 任一边置信度都要大于阈值

        if (threshold is not None) and any((scores[0]<threshold,scores[1]<threshold)):
            flag=False
        if flag:
            new_pair.append(pair)
        else:
            trash_pair0=f"score={scores[0]:.3f}, label={labels[0]}, text={a}\n "
            trash_pair1=f"score={scores[1]:.3f}, label={labels[1]}, text={b}\n"
            pair=(trash_pair0,trash_pair1)
            trash_pair.append(pair)
        if report_neg and not flag:
            print('-----------------------------------------')
            print(labels,scores)
            print([pair[0].lower(),pair[1].lower()])

    print(f'lang id filter| [{len(new_pair)}/{len(text_pair_ls)}] samples retained, [{len(text_pair_ls)-len(new_pair)}/{len(text_pair_ls)}] were deleted.')
    return new_pair,trash_pair

if __name__ == '__main__':
    print(f"python {sys.argv[0]} --src-lang  --tgt-lang --in-prefix  --out-prefix --remove-bpe(optional) --wt(optional)")
    parser = argparse.ArgumentParser(description="Lang id filter")
    parser.add_argument('--src-lang',type=str,default='zh',required=True)
    parser.add_argument('--tgt-lang',type=str,default='en',required=True)
    parser.add_argument('--in-prefix',type=str,default=None,required=True)
    parser.add_argument('--out-prefix',type=str,default=None,required=True)
    parser.add_argument('--remove-bpe',action="store_true",help="remove bpe when get language score")
    parser.add_argument('--threshold',type=float,default=None)
    parser.add_argument('--wt',action="store_true",help="write trash to outprefix.trash.lang")
    args = parser.parse_args()

    src_file, tgt_file=f"{args.in_prefix}.{args.src_lang}",f"{args.in_prefix}.{args.tgt_lang}"
    out_src_file, out_tgt_file=f"{args.out_prefix}.{args.src_lang}",f"{args.out_prefix}.{args.tgt_lang}"
    pairs=read_text_pair(src_file,tgt_file)
    new_pair_lang,trash_pair=lang_id_filter(pairs,model_path='lid.176.bin',
                                 src_lang=args.src_lang,
                                 tgt_lang=args.tgt_lang,
                                 threshold=args.threshold,
                                 remove_bpe=args.remove_bpe)
    write_text_pair(new_pair_lang,out_src_file=out_src_file,out_tgt_file=out_tgt_file)

    # write trash
    if args.wt:
        out_src_file, out_tgt_file = f"{args.out_prefix}.trash.{args.src_lang}", f"{args.out_prefix}.trash.{args.tgt_lang}"
        write_text_pair(trash_pair, out_src_file=out_src_file, out_tgt_file=out_tgt_file)
