import os
import sys
import time
import logging
from tqdm import tqdm
logger=logging.getLogger('cut')
logger.setLevel(logging.DEBUG)
from pythainlp import word_tokenize
# words = word_tokenize(sent,keep_whitespace=False)

def read_file(file,t2s=False):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    if t2s:
        import zhconv
        lines = [zhconv.convert(sent.strip(), "zh-cn") for sent in lines]
    else:
        lines = [line.strip() for line in lines]
    # print(f'read  {file} success, total {len(lines)} lines.')

    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')


def process():
    infile=sys.argv[1]
    outfile=sys.argv[2]

    lines=read_file(infile, t2s=True)
    res=[]
    for line in lines:
        words = word_tokenize(line,keep_whitespace=False)
        new_line = " ".join(words) + "\n"
        res.extend(new_line)
    write_file(res,outfile)


if __name__ == '__main__':
    assert len(sys.argv)==3,f"usage: python {sys.argv[0]} <infile> <outfile> "
    process()
    logger.info("all done!")