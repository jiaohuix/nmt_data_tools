'''
usage: merge src and tgt to  'src ||| tgt ' for fast_align input
'''
import sys
def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def merge(src_path,tgt_path):
    # read file
    src_lines = read_file(src_path)
    tgt_lines = read_file(tgt_path)
    res=[]
    for src, tgt in zip(src_lines, tgt_lines):
        src, tgt = src.strip(), tgt.strip()
        text = f"{src} ||| {tgt}\n"
        res.append(text)
    return res


if __name__=="__main__":
    assert len(sys.argv) == 4, f"usage: python {sys.argv[0]} <src_file> <tgt_file> <outfile>"
    src_file=sys.argv[1]
    tgt_file=sys.argv[2]
    outfile=sys.argv[3]

    res=merge(src_file,tgt_file)
    write_file(res,file=outfile)

