import os
import sys
import json

def load_save(in_path,out_path):
    with open(in_path,'r',encoding='utf-8') as f:
        data=json.load(f)
        keys=list(data.keys())
        keys=['<s>','<pad>','</s>','<unk>']+keys[3:]

    with open(out_path,'w',encoding='utf-8') as f:
        f.write('\n'.join(keys)+'\n')
    print(f'write to {out_path} success.')


if __name__ == '__main__':
    assert len(sys.argv)==3,f"usage: python {sys.argv[0]} <infile> <outfile>"
    infile=sys.argv[1]
    outfile=sys.argv[2]
    load_save(infile,outfile)