'''
transfer paddle vocab to fariseq dict
paddle :
    <s>
    <pad>
    </s>
    <unk>
    a
    b
    c
fairseq:
    a 10
    b 9
    c 8
'''
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

def vocab2dic(in_file,out_file):
    vocab=read_file(in_file)[4:]
    freq=[100000-i for i in range(len(vocab))]
    lines=[f"{v.strip()} {f}\n" for v,f in zip(vocab,freq)] # 空格划分
    write_file(lines,out_file)

if __name__ == '__main__':
    assert len(sys.argv)==3,f"usage: python {sys.argv[0]} <infile>(vocab.lang) <outfile>(dict.lang.txt)"
    infile=sys.argv[1]
    outfile=sys.argv[2]
    vocab2dic(in_file=infile,out_file=outfile)