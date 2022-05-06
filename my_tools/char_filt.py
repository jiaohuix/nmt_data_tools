import sys
from tqdm import tqdm
import argparse

def read_text(src_file):
    with open(src_file,'r',encoding='utf-8') as f:
        lines=[line.strip() for line in f.readlines()]
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.write('\n'.join(res)+"\n")
    print(f'write to {file} success.')


if __name__ == '__main__':
    path="vocab.en"
    