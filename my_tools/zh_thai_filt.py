'''
不考虑翻译标签本身错误的情况！

处理中泰数据
        1、中文含特殊标记，如{} √
        2、中英文混杂 ，删除连续英文字符
        3、含乱码  ->  变成" "+\n   √
        4、中文繁体字


        ikcest： !!!!!! 【注意：ikcest的数据不要处理，因为test也包含这些乱七八糟的符号】
            大量\n
            ◆
            \<.*?\>
            #item_#\*、
            #item_#\*
'''
import re
import sys
from tqdm import tqdm
import argparse
import zhconv
from pythainlp import word_tokenize
import hashlib


def get_hashes(raw_line):
    hash = hashlib.md5(raw_line.encode()).hexdigest()
    return hash


def read_text(file):
    with open(file,'r',encoding='utf-8') as f:
        lines=[line.strip() for line in f.readlines()]
    return lines

def write_file(res,file):
    with open(file,'w',encoding='utf-8') as f:
        f.writelines(res)
    print(f'write to {file} success, total {len(res)} lines.')


'''
278)\fn方正准圓簡體\bord0\fs20\cH24efff}宇宙大探索 {\fs17\cHffffff} 第一集
-美國總統來訪 300)\3cHD5D9C6\cHFFFFFF}距 圣 誕 四 周

泰: /c.bg_transparent
c.bg_transparent

221)}狀態： 紐約警局任職 你永遠找不到我們
但無論是受害人還是行兇者
只要你的號碼被列出來 我們就會找到你
79)}格里芬競選市長
新的市長候選人
地方檢察官助理蘭登·沃克
這是割喉戰
58)}市長競選白熱化
213)}音頻攔截 預付費手機
87)}格里芬募款方式遭抨擊 那名記者 瑪克辛·安吉拉斯
103)}格里芬募款方式遭抨擊
66)}記者
192)獲取

包含数字的翻译全都错误了，不一定，先不动吧。省的错删除。之后成对处理
 ♪


เธเธณเนเธกเนเธกเนเธขเธญเธกเนเธงเนเนเธ
เธเธฑเธเธเนเนเธเนเธเธขเธฒเธขเธฒเธกเธซเธฒเธเธฒเธเธเธตเนเธเธฐเธเธฅเธฑเธเธเนเธฒเธ
เธเธฑเธเธเธฑเธเธเธฒเธฃเนเธเธญเนเธเนเธเนเธฒ
这是啥
เธฅเธตเธญเธฒเธซเน เธกเธตเนเธเธฃเธซเธฒเธเธธเธเธเธฒเธเธชเธฒเธขเธ เธฒเธเธเธทเนเธเธเธดเธ
เธชเธฒเธขเธเธธเธเนเธเธดเธ เนเธญเธฒเธกเธญเธฃเนเธเธตเธเนเธซเนเนเธเธฒเธเนเธงเธขเนเธเนเนเธซเธก?
เนเธเน.
เนเธกเธเน?
เนเธฎเน เธเธกเนเธเธตเธขเธเนเธเธฃเธกเธฒเนเธเนเธ
เธเธตเนเธฃเธฑเธ เธงเธฑเธเธเธตเนเธเธญเธเธเธธเธเนเธเนเธเนเธ?
เธเธต เนเธเนเธกเธฑเธเธขเธธเนเธเธกเธฒเธ
เธเธตเนเธฅเนเธง
เนเธฅเนเธงเธเธธเธเธฅเนเธฐ?
เธเนเธขเธธเนเธเธญเธขเธนเน
เธเธธเธเนเธกเนเนเธเนเธเนเธฃเธเธฐ?
เนเธเน, เธเธฑเธเนเธเธดเนเธ, เธเธฑเธ, เธเธฑเธเธเนเธญเธเธญเธขเธนเนเธเธณเธเธฒเธเธเธเธเธถเธ
เนเธเน เธเธกเธเนเนเธซเธกเธทเธญเธเธเธฑเธ
เธเธธเธเธเธฐเธเธฅเธฑเธเธกเธฒเธเนเธฒเธเนเธซเธกเธเธทเธเธเธตเน?
เนเธเนเธเธญเธ.
เนเธฃเธฒเธกเธตเธเธฑเธเธเธฑเธเธเธฐ เธเธณเนเธเนเนเธซเธก?
เนเธฎเน เธเธกเธเนเธญเธเนเธเนเธฅเนเธง
เธเธธเธเธเนเธฃเธนเน เธเธฒเธเนเธญเธเธชเธฒเธฃเธเธงเธเธเธตเนเธกเธฑเธเธเนเธฒเนเธเธทเนเธญเธเธฐ
เนเธญเนเธ



泰语也夹杂英语
♪ We need each other to raise us up เราต่างต้องการผู้อื่นเพื่อเลี้ยงดูเรา


'''
def symbolFilter(text):
    fix_rule=[
        r"{\cHFFFFFF}{\3cH111111}{\4cH111111}",
        r"{\fn方正黑體簡體\fs18\b1\bord1\shad1\3cH2F2F2F}",
        r"{\fn黑体\fs22\bord1\shad0\3aHBE\4aH00\fscx67\fscy66\2cHFFFFFF\3cH808080}",
        r"{\cHFFFFFF}{\3cH111111}{\4cH111111}",
        r"{\fn方正黑体简体\fs18\b1\bord1\shad1\3cH2F2F2F}",
        r"{\fnCronos Pro Subhead\fs14\1cH3CF1F3}",
        r"{\cHFFFFFF}{\3cH111111}{\4cH111111}",
        r"{\fn方正黑体简体\fs18\b1\bord1\shad1\3cH2F2F2F}",
        "■",
        "▌",
        "█",
        "♪",
        r"{\fn黑体\fs22\bord1\shad0\3aHBE\4aH00\fscx67\fscy66\2cHFFFFFF\3cH808080}",
        r"{\3cH202020}",
        "/c.bg_transparent",
        "c.bg_transparent"
    ]
    patterns=[
        "^\{.*?\}",
        "\{.*?\}",
        r"\\.*?\}",
        "^- ",
        "^-"# 泰语也要处理
    ]

    for rule in fix_rule:
        text=text.replace(rule,"")

    for pattern in patterns:
        text=re.sub(pattern,"",text)
    return text


def check_is_encode_error(string):
    try:
        string.encode('gbk')
    except UnicodeEncodeError:
        return True
    return False

def is_all_chinese(strs):
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True

def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def delete_en_from_zh(sent,k=2):
    # tolerant for k words
    new_sent=""
    alpha_cont=0 # 超过2就要删除
    temp=""
    sent=sent.split()
    for word in sent:
        if is_contains_chinese(word):
            if alpha_cont<=k:
                new_sent+=temp # 把以前的加上
            temp=" "
            new_sent+=word
            alpha_cont=0 # 重新计数
        else: # 字母
            alpha_cont+=1
            temp+=word+" "
    return new_sent

def is_contains_en(word):
    my_re = re.compile(r'[A-Za-z]', re.S)
    res = re.findall(my_re, word)
    if len(res):
        return True
    else:
        return False

def delete_en_from_other(sent,k=2):
    # tolerant for k words
    new_sent=""
    alpha_cont=0 # 超过2就要删除
    temp=""
    sent=sent.split()
    for word in sent:
        if not is_contains_en(word):
            if alpha_cont<=k:
                new_sent+=temp # 把以前的加上
            temp=" "
            new_sent+=word
            alpha_cont=0 # 重新计数
        else: # 字母
            alpha_cont+=1
            temp+=word+" "
    return new_sent


def check_is_error_thai(text):
    symbols=["","","","","",""]
    for symbol in symbols:
        if symbol in text:
            return True
    return False

def process_zh(in_file):
    print("Processing zh...")
    # read
    lines=read_text(in_file)

    # clean
    res=[]
    err_num=0
    for i,line in tqdm(enumerate(lines)):
        line=line.strip()
        # 1.error code
        if check_is_encode_error(line):
            res.append("\n")
            err_num+=1
            continue
        elif i<len(lines)-2 and (check_is_encode_error(lines[i+1]) or check_is_encode_error(lines[i+2])):
            # delete error code that are considered correct
            res.append("\n")
            err_num+=1
            continue

        # 2.filter out sumbol
        line=symbolFilter(line)
        # 3.traditional to simplified
        line = zhconv.convert(line, 'zh-cn')
        # 4.filter out long english sequence
        line = delete_en_from_zh(line,k=2) # delete english sentence which length>2
        line = line.strip()+"\n"
        res.append(line)

    print(f"Error lines:[{err_num}/{len(res)}] ({err_num/len(res):.3f})")

    return res


def process_thai(in_file):
    print("Processing thai...")
    # read
    lines=read_text(in_file)

    # clean
    res=[]
    err_num=0
    for i,line in tqdm(enumerate(lines)):
        line=line.strip()
        # 1.error code
        if check_is_error_thai(line):
            res.append("\n")
            err_num+=1
            continue
        elif i<len(lines)-2 and (check_is_error_thai(lines[i+1]) or check_is_error_thai(lines[i+2])):
            # delete error code that are considered correct
            res.append("\n")
            err_num+=1
            continue

        # 2.filter out sumbol
        line=symbolFilter(line)
        # 3.filter out long english sequence
        line = delete_en_from_other(line,k=2) # delete english sentence which length>2
        # 4.thai tokenize
        # line=" ".join(word_tokenize(line,keep_whitespace=False))
        line = line.strip()+"\n"
        res.append(line)

    print(f"Error lines:[{err_num}/{len(res)}] ({err_num/len(res):.3f})")
    return res



def process_pair(th_lines,zh_lines):
    print("Processing pair...")
    assert len(th_lines)==len(zh_lines)
    # 去空，去重
    res_th,res_zh=[],[]
    seen=set()
    for th_line,zh_line in tqdm(zip(th_lines,zh_lines)):
        th_line,zh_line = th_line.strip(),zh_line.strip()
        # 去空
        if th_line=="" or zh_line=="": continue
        # 去重
        hash_code = get_hashes(raw_line=th_line+zh_line)

        if hash_code not in seen:
            seen.add(hash_code)
            res_th.append(th_line+"\n")
            res_zh.append(zh_line+"\n")
    print(f"Final lines:[{len(res_th)}/{len(th_lines)}] ({len(res_th)/len(th_lines):.3f})")
    return res_th,res_zh

if __name__ == '__main__':
    assert len(sys.argv)==5,f"usage: python {sys.argv[0]} <in_prefix> <out_prefix> <th_suffix> <zh_suffix>"
    in_prefix=sys.argv[1]
    out_prefix=sys.argv[2]
    th_suffix=sys.argv[3]
    zh_suffix=sys.argv[4]

    file_in_th=f"{in_prefix}.{th_suffix}"
    file_in_zh=f"{in_prefix}.{zh_suffix}"
    file_out_th=f"{out_prefix}.{th_suffix}"
    file_out_zh=f"{out_prefix}.{zh_suffix}"

    print(file_in_zh,file_out_th,file_out_zh,file_out_th)
    th_lines=process_thai(file_in_th)
    zh_lines=process_zh(file_in_zh)
    th_lines,zh_lines=process_pair(th_lines,zh_lines)

    write_file(th_lines,file=file_out_th)
    write_file(zh_lines,file=file_out_zh)
