import os
import sys
skip_words=['<s>','<pad>','</s>','<unk>']

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

def dic2vocab(in_file,out_file):
    dic=read_file(in_file)
    words=[d.strip().split(' ')[0] for d in dic]
    words=skip_words+words
    words=[w+'\n' for w in words]
    write_file(words,out_file)

if __name__ == '__main__':
    assert len(sys.argv)==3,f"usage: python {sys.argv[0]} <infile>(dict.lang.txt) <outfile>(vocab.lang)"
    infile=sys.argv[1]
    outfile=sys.argv[2]
    dic2vocab(in_file=infile,out_file=outfile)
