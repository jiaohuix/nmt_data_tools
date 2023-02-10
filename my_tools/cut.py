import os
import sys
import time
import logging
from tqdm import tqdm
logger=logging.getLogger('cut')
logger.setLevel(logging.DEBUG)

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
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
    backend=sys.argv[3] if len(sys.argv)>=4 else "jieba"
    userdict=sys.argv[4] if len(sys.argv)>=5 else ""

    if not os.path.exists(userdict):
        userdict=None
        userdict_ls=[]
    else:
        userdict_ls = read_file(userdict)
        print(f"------loading userdict {userdict}...------")

    assert backend in ["jieba", "thulac", "ltp"]
    print(f"segment backend: {backend}.")

    if backend=="thulac":
        import thulac
        thu = thulac.thulac(seg_only=True,T2S=True,user_dict=userdict)
        thu.cut_f(infile, outfile)  # 对input.txt文件内容进行分词，输出到output.txt
    else:
        lines=read_file(infile)
        res=[]
        if backend=="ltp":
            from ltp import LTP
            ltp = LTP()  # 默认加载 Small 模型
            # 4.2 版本的 ltp 暂时还没有加入该 api，可以使用 add_words 来加入自定义词语
            # ref: https://github.com/HIT-SCIR/ltp/issues/618
            # ltp.init_dict(path=userdict)
            ltp.add_words(words=userdict_ls)
            output = ltp.pipeline(lines, tasks=["cws"])
            res = [" ".join(words) + "\n" for words in output.cws]
        elif backend=="jieba":
            import zhconv
            import jieba
            jieba.load_userdict(userdict_ls)
            for sent in tqdm(lines):
                sent = zhconv.convert(sent.strip(), "zh-cn")
                sent = " ".join(jieba.lcut(sent))+"\n"
                res.append(sent)
        write_file(res,outfile)


if __name__ == '__main__':
    assert len(sys.argv)>=3,f"usage: python {sys.argv[0]} <infile> <outfile> <backend> <userdict>"
    process()
    logger.info("all done!")