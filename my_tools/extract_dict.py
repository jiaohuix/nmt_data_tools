'''
usage: extract bilingual dict with align frequence after fast_align
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


def get_dict(text_path="text.fr-en",align_path="fr-en.align",topk=10):
        # read file
        text_lines=read_file(text_path)
        align_lines=read_file(align_path)
        # word count
        word_dict={}
        for text,align in zip(text_lines,align_lines):
                text,align = text.strip(),align.strip()
                src_text,tgt_text = text.split(" ||| ")
                src_text,tgt_text = src_text.split(),tgt_text.split()
                for pair in align.split():
                        src_id,tgt_id = pair.split("-")
                        src_id,tgt_id = int(src_id),int(tgt_id)
                        tup=(src_text[src_id],tgt_text[tgt_id])
                        word_dict[tup]=word_dict.get(tup,0)+1
        # sort dict
        sorted_dict=sorted(word_dict.items(),key=lambda item:item[1],reverse=True)
        print(f"words: {len(sorted_dict)}")
        # topk
        res=[]
        for tup in sorted_dict[:topk]:
                pair,cnt = tup
                src,tgt = pair
                text=f"{src}\t{tgt}\t{cnt}\n"
                res.append(text)
        return res

if __name__=="__main__":
    assert len(sys.argv) == 5, f"usage: python {sys.argv[0]} <text_file> <align_file> <outfile> <topk>"
    text_file=sys.argv[1]
    align_file=sys.argv[2]
    outfile=sys.argv[3]
    topk=int(sys.argv[4])

    res=get_dict(text_file,align_file,topk)
    write_file(res,file=outfile)

