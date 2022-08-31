import os
import sys

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')


if __name__ == '__main__':
    assert len(sys.argv)==3,f"usage: python {sys.argv[0]} <infile> <outfile>"
    infile=sys.argv[1]
    outfile=sys.argv[2]
    lines =read_file(infile)
    lines = [" ".join(line.strip().split()[1:])+'\n' for line in lines]
    write_file(lines,outfile)
