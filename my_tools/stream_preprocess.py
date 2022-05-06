import jieba
import sys
def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.write(''.join(res))
    print(f'write to {file} success.')


def stream2whole(lines):
    ''' 输入流式的文本，输出整句文本（减少了行数），可正常使用'''
    last_line=''
    res=[]
    for line in lines:
        line=line.strip()
        if len(line)<=len(last_line) and not line.startswith(last_line): # 重置了，将上一句话加入结果
            res.append(last_line+'\n')
        last_line=line
    res.append(last_line+"\n")
    return res

def is_all_chinese(strs):
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True

def special_case_fn(token):
    ''' return word list '''
    special_tokens = [",", ".", "-", ":", "(", ")", "\'", "\"", "*", ";", "$", "&"]
    for sp in special_tokens:
        if sp in token:
            token=f" {sp} ".join(token.split(sp))
    return token.split()

def whole2stream(lines,lang='zh'):
    ''' 将整句转为流式，问题在于如何检测出中英文混杂时的中文，功能不完善 '''
    res=[]
    for line in lines:
        # 对中文文本分词，区分出英文
        if lang=='zh':
            words=jieba.lcut(line.strip())
            # 将中文分成字
            char_ls=[]
            for word in words:
                ls=list(word) if is_all_chinese(word) else [word]
                char_ls.extend(ls)
            words=char_ls
        # 英文等直接split,要处理特殊符号
        else:
            raw_words=line.strip().split()
            words=[]
            for word in raw_words:
                words.extend(special_case_fn(word))
        # 增长式记录，中文不用将字分开
        for i in range(1,len(words)+1):
            if lang=='zh':
                res.append("".join(words[:i])+"\n")
            else:
                res.append(" ".join(words[:i])+"\n")
    return res



if __name__ == '__main__':
    '''
    流式转非流式：  python utils/stream_preprocess.py enes21/en-es.stream.500.src.txt dev500.en 1 en
    非流式转流式：  python utils/stream_preprocess.py dev500.en  stream.en 2 en
    '''
    assert len(sys.argv)==5,f"usage: python {sys.argv[0]} <infile> <outfile> <1(towhole)|2(tostream)> <lang>"
    infile=sys.argv[1]
    outfile=sys.argv[2]
    mode=sys.argv[3]
    lang=sys.argv[4]
    lines = read_file(infile)
    res=[]
    if int(mode)==1:
        res=stream2whole(lines)
    elif int(mode)==2:
        res=whole2stream(lines,lang=lang)
    write_file(res,file=outfile)
