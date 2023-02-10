import os
import sys
import time
import logging
from tqdm import tqdm
logger=logging.getLogger('cut')
logger.setLevel(logging.DEBUG)

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

def batch_process(data,fn, bsz=128, log_interval=10):
    res = []
    start = 0
    i = 0

    start_time = time.time()
    total_len = len(data)
    steps = total_len // bsz
    while start + bsz - 1 < total_len:
        # caculate score
        cur_data = data[start:(start + bsz) :]
        output = fn(cur_data)
        res.append(output)
        start += bsz
        i += 1

        # timer
        exe_time = time.time() - start_time
        avg_exe_time = exe_time / i
        eta_time = (steps - i) * avg_exe_time
        if i % log_interval == 0:
            print(f"processed: [{i}/{steps}], eta: {eta_time:.3f} s.")

    # tail score
    if start < total_len:
        cur_data = data[start:total_len :]
        output = fn(cur_data)
        res.append(output)
    return res


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
        lines=read_file(infile, t2s=True)
        res=[]
        if backend=="ltp":
            from ltp import LTP
            from functools import partial
            ltp = LTP()  # 默认加载 Small 模型
            # 4.2 版本的 ltp 暂时还没有加入该 api，可以使用 add_words 来加入自定义词语
            # ref: https://github.com/HIT-SCIR/ltp/issues/618
            # ltp.init_dict(path=userdict)
            ltp.add_words(words=userdict_ls)
            seg_ltp_fn = partial(ltp.pipeline, tasks=["cws"])
            outs = batch_process(lines,fn=seg_ltp_fn,bsz=128, log_interval=10) # ltp默认用多核，应该一次给一批数据
            for out in outs:
                cur_res = [" ".join(words)+"\n" for words in out.cws]
                res.extend(cur_res)

        elif backend=="jieba":
            import jieba
            jieba.load_userdict(userdict_ls)
            for sent in tqdm(lines):
                sent = " ".join(jieba.lcut(sent))+"\n"
                res.append(sent)
        write_file(res,outfile)


if __name__ == '__main__':
    assert len(sys.argv)>=3,f"usage: python {sys.argv[0]} <infile> <outfile> <backend> <userdict>"
    process()
    logger.info("all done!")