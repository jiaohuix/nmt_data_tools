import os
import sys
import time
import logging
from tqdm import tqdm
from pythainlp import word_tokenize
logger=logging.getLogger('cut')
logger.setLevel(logging.DEBUG)

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

res = []
def process(sent):
    sent=sent.strip()
    sent=word_tokenize(sent,keep_whitespace=False)
    sent=' '.join(sent)+'\n'
    res.append(sent)
    return sent

if __name__ == '__main__':
    assert len(sys.argv)==3,f"usage: python {sys.argv[0]} <infile> <outfile>"
    infile=sys.argv[1]
    outfile=sys.argv[2]
    lines=read_file(infile)
    for line in tqdm(lines):
        process(line)
    write_file(res,outfile)
