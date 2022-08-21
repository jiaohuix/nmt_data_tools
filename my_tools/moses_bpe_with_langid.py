'''
args: lang, bpe_code, infile out file ,use moses
'''
import sys
import jieba
from subword_nmt import subword_nmt
from sacremoses import MosesTokenizer
from tqdm import tqdm

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')

class Tokenizer:

    def __init__(self, bpe_dict, lang):
        bpe_parser = subword_nmt.create_apply_bpe_parser()
        bpe_args = bpe_parser.parse_args(args=['-c', bpe_dict])
        self.bpe = subword_nmt.BPE(bpe_args.codes, bpe_args.merges,
                                   bpe_args.separator, None,
                                   bpe_args.glossaries)
        self.lang = lang
        self.is_chinese = lang == "zh"
        self.moses_tok = MosesTokenizer(lang=lang) if not self.is_chinese else None

    def tokenize(self, raw_string):
        """
        Tokenize string(BPE/jieba+BPE)
        """
        raw_string = raw_string.strip('\n')
        if not raw_string:
            return raw_string
        if self.is_chinese:
            raw_string = " ".join(jieba.cut(raw_string))
        else:
            raw_string=" ".join(self.moses_tok.tokenize(raw_string))
        bpe_str = self.bpe.process_line(raw_string)
        return " ".join(bpe_str.split())

def tokenize(lines,bpe_code):
    res=[]
    for line in tqdm(lines):
        line = line.strip()
        lang_token = line.split()[0]
        lang = lang_token.replace("<","").replace(">","")
        line = " ".join(line.split()[1:])

        tokenizer = Tokenizer(bpe_dict=bpe_code, lang=lang)
        line = tokenizer.tokenize(raw_string=line)
        res.append(f"{lang_token} {line}\n")
    return res


if __name__ == '__main__':
    # args: lang, bpe_code, infile out file
    assert len(sys.argv)==4,f"usage: python {sys.argv[0]} <infile> <outfile> <bpe_code_path> (infile contains prepend langid,like <de> xxx )"
    infile=sys.argv[1]
    outfile=sys.argv[2]
    bpe_code=sys.argv[3]
    # lang=sys.argv[4]

    lines= read_file(infile)
    res=tokenize(lines,bpe_code)
    write_file(res,file=outfile)
