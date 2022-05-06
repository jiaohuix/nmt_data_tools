import json
def read_streams(infile):
    src_js = [[]]
    with open(infile, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            txt = line.strip()
            if len(src_js[-1]) == 0 or txt.startswith(src_js[-1][-1][-1]) is False:
                src_js[-1].append([])
            src_js[-1][-1].append(txt)
    return src_js

def write2json(res,out_file):
    with open(out_file,'w',encoding='utf-8') as f:
        json.dump(res,f,ensure_ascii=False)


if __name__ == '__main__':
    path='en-es.stream.500.src.txt'
    res=read_streams(path)
    write2json(res,'en-es.dev.en.json')
