import sys
from tqdm import tqdm

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines= f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def extract_text(lines,indices):
    res = []
    for idx in tqdm(indices):
        idx = int(idx.strip())
        res.append(lines[idx])
    return res

if __name__ == '__main__':
    assert len(sys.argv)==4,f"usage: python {sys.argv[0]} <textfile> <idxfile> <outfile>"
    textfile = sys.argv[1] # text
    idxfile = sys.argv[2] # idxfile
    outfile = sys.argv[3]

    lines = read_file(textfile)
    indices = read_file(idxfile)
    res = extract_text(lines,indices)

    write_file(res,outfile)

