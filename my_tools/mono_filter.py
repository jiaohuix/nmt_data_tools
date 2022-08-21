import sys
import fasttext
from tqdm import tqdm
import argparse

def read_text(src_file):
    with open(src_file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def lang_id_filter(lines,model_path,lang='zh',threshold=0.5):
    model=fasttext.load_model(model_path)
    new_lines=[]
    for line in lines:
        labels,scores=model.predict([line.strip().lower()])

        label=[label[0].replace('__label__','') for label in labels][0]
        score=[float(score) for score in scores][0]
        # src和tgt标签都要正确
        flag=True if label==lang else False
        # 任一边置信度都要大于阈值
        if score<threshold:
            flag=False
        # if not flag:
        #     print(f"wrong lang: {line}")
        if flag:
            new_lines.append(line)

    print(f'lang id filter| [{len(new_lines)}/{len(lines)}] samples retained, [{len(lines)-len(new_lines)}/{len(lines)}] were deleted.')
    return new_lines

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Lang id filter")
    parser.add_argument('--lang',type=str,default='zh')
    parser.add_argument('--in-prefix',type=str,default=None)
    parser.add_argument('--out-prefix',type=str,default=None)
    parser.add_argument('--threshold',type=float,default=0.5)
    args = parser.parse_args()

    src_file=f"{args.in_prefix}.{args.lang}"
    out_src_file=f"{args.out_prefix}.{args.lang}"
    lines=read_text(src_file)
    new_lines=lang_id_filter(lines,model_path='lid.176.bin',lang=args.lang,threshold=0.2)
    write_file(new_lines,out_src_file)

