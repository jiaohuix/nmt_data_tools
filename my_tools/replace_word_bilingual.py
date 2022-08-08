'''
modify:Not just use English as the source sentence
1. dict, lang pair
2. lang en
需求：
1. 根据输入的句子语言token，来确定所属语言和需要替换的词。支持多种词典 √
2. 支持单语
3. 写个demo，合到tools（单例，抽取词典）
4. 全流程： tok、clean、bpe、ras
    (1) tokenize (jieba moses)
    (2) clean (lang id,length)
    (3) learn apply bpe
    (4) prepend lang token
    (5) (merge) raw_train: X4
            # Bidirection
            cat train.de  train.en >train.src
            cat train.en  train.de >train.tgt
            # Monolingual
            cat train.de  >> train.src && cat train.de >> train.tgt
            cat train.en  >> train.src && cat train.en >> train.tgt
            src tgt / tgt src / src src / tgt tgt
    (6) ras:
            python replace_word_bilingual.py --langs de;en --dict-path dic --data-path data2 --prefix train --num-repeat 1 --moses-detok
            return:
                expanded_train.src
                expanded_train.src
    (7) moses tokenize + bpe (expanded_train.src)
    (8) merge [raw_train] and [expanded_train]
        subsample valid
    (9) shuffle
5. 改进： target添加对应的mask。还有两端随机mask

'''

import os
import random
from collections import defaultdict
import argparse
from pprint import pprint
import time
from tqdm import tqdm
random.seed(1)

parser = argparse.ArgumentParser()
parser.add_argument('--langs', required=True, help="The iso 639-2 code of languages that we apply RAS."
                                                   " We use MUSE dictionary for each en-x pair.") # en-de.txt
parser.add_argument('--dict-path', required=True) # / en-X.txt bilingual dict
parser.add_argument('--data-path', required=True) # parallel corpus dir, /train.src train.tgt
parser.add_argument('--prefix', type=str,default="train", help="replace file, prefix.src/tgt ,default=train")
parser.add_argument('--num-repeat', type=int, default=1)
parser.add_argument('--moses-detok',action="store_true",help="wthether to use moses detokenizer.(except chinese)")
parser.add_argument('--replace-prob', type=float, default=0.3)
parser.add_argument('--vocab-size', type=int, default=30000)
args = parser.parse_args()
pprint(args)

# langs = [l for l in args.langs.split(";") if l != "en"]
langs = [l for l in args.langs.split(",")]
dict_path = args.dict_path
data_path = args.data_path
use_moses_detok = args.moses_detok
prefix = args.prefix


# remove bpe
def remove_bpe(input_sentence, bpe_symbol="@@ "):
    """

    :param input_sentence: the input sentence that is processed by bpe sub-word operation.
    :param bpe_symbol: the bpe indicator(default: '@@ '), which will be removed after the `remove_bpe` function
    :return: the output sentence that is recovered from  sub-word operation.
    """
    _sentence = input_sentence.replace("\n", '')
    _sentence = (_sentence + ' ').replace(bpe_symbol, '').rstrip()
    return _sentence + "\n"

def detokenize():
    pass


# read dictionaries
def load_dicts(dictionary_path, languages, sep=" "):
# def load_dicts(dictionary_path, languages, sep="\t"):
    """

    :param dictionary_path: the path of the root of MUSE dictionaries
    :param languages: en-x dictionaries will be used for all x in `languages`
    :return: a dictionary of dictionaries that stores all word pairs for all en-x in `languages`
    原来：英文为中心
    修改：读取任两对，构建双向的词典，最好兼容多种语言。读取path里面的词典，确保languages所有语言都有
    """
    files = os.listdir(dictionary_path)

    def isValidDic(name, languages):
        flag = True
        if not name.endswith(".txt"): flag = False
        if len(name.replace(".txt", "").split("-")) != 2: flag = False
        lang_pair = name.replace(".txt", "").split("-")
        if flag and any((lang_pair[0] not in languages, lang_pair[1] not in languages)): flag = False
        return flag

    files = [file for file in files if isValidDic(file,languages)]
    dict_of_dict = {}
    for file in files:
        pair = file.replace(".txt", "").split("-")
        pair_name_xy=f"{pair[0]}-{pair[1]}"
        pair_name_yx=f"{pair[1]}-{pair[0]}"
        x2y_dict = defaultdict(list)
        y2x_dict = defaultdict(list)
        with open(os.path.join(dictionary_path,file), encoding='utf-8') as f:
            i = 0
            for _line in f:
                bi_text = _line.strip().split(sep)
                assert len(bi_text) == 2, ("in file {}/{}, line index {} has an invalid number of columns {}"
                                           .format(dictionary_path, pair_name_xy, i, len(bi_text)))
                x2y_dict[bi_text[0]].append(bi_text[1])
                y2x_dict[bi_text[1]].append(bi_text[0])
                if i >= args.vocab_size:
                    # only keep first `vocab_size` word pairs
                    break
                i += 1
        dict_of_dict[pair_name_xy] = x2y_dict
        dict_of_dict[pair_name_yx] = y2x_dict
        """
        这个list是指x到y有多个近义词
        defaultdict(<class 'list'>, {'I': ['Ich'], 'We': ['Wir'], 'The': ['Die'], 'They': ['Sie'], 'This': ['Das'], 'He': ['Er'], 'percent': ['prozent'], 'What': ['Was']})
        }
        """
    return dict_of_dict



# replace tokens in one sentence
def replace_one_sent(tokens, dictionary):
    """

    :param tokens:
    :param dict: is a default dict with list as key
    :return:


    eg: en-de.txt  dic:{"en":"de"}?
    """
    cnt = 0 # 替换的单词数
    new_tokens = []
    for token in tokens:
        if token in dictionary and random.random() < args.replace_prob:
            new_tokens.append(random.choice(dictionary[token]))
            cnt += 1
        else:
            new_tokens.append(token)

    return new_tokens, cnt


# from one sentence we get several copies
def replace_sent(sentence,src_lang_tok, dictionaries):
    """

    :param sentence: list of token in the sentence
    :param dictionaries: all dictionaries
    :param langs: all languages involved
    :return:
    """
    replace_cnt = 0
    total_token = 0
    replaced_sents = []
    # 从dict里含的 src_lang_tok2X中随机选repeat个
    pair_names = list(dictionaries.keys())
    exist_langs = [name.split("-")[1] for name in pair_names if name.split("-")[0]==src_lang_tok]
    # selected_langs = random.sample(exist_langs, args.num_repeat)
    selected_langs = [random.sample(exist_langs,1)[0] for _ in range(args.num_repeat)]
    # randomly select `num_repeat` languages from the list, create `num_repeat` copies for each sentence
    for _lang in selected_langs:
        dict_name = f"{src_lang_tok}-{_lang}"
        assert dict_name in dictionaries, ("{} not in dictionaries!".format(dict_name))
        selected_dict = dictionaries[dict_name]
        new_sent, cnt = replace_one_sent(sentence, selected_dict)
        if cnt > 0: # 句子有被替换
            replaced_sents.append(new_sent)
        replace_cnt += cnt
        total_token += len(new_sent)

    return replaced_sents, replace_cnt, total_token


if __name__ == "__main__":
    # 1. remove-bpe
    if not os.path.exists(os.path.join(data_path, "removed_bpe_file.src")):
        print("======[Remove bpe ing...]======")
        with open(os.path.join(data_path, f"{prefix}.src"), 'r',encoding='utf-8') as f, \
                open(os.path.join(data_path, "removed_bpe_file.src"), 'w+',encoding='utf-8') as fw:
            for line in tqdm(f):
                new_line = remove_bpe(line, "@@ ")
                lang = new_line.split()[0].replace("<","").replace(">","")
                assert lang in langs, "language token should in langs config."
                if use_moses_detok and lang!="zh":
                    new_line = " ".join(new_line.split()[1:])
                    from sacremoses import MosesDetokenizer
                    detok = MosesDetokenizer(lang=lang)
                    new_line = f"<{lang}> " + detok.detokenize(new_line.strip().split())+"\n"
                fw.write(new_line)



    # 2. load dictionaries
    print("======[Loade Dicts ing... ]======")
    dicts = load_dicts(dict_path, langs)
    print(dicts.keys()) # lang pair

    for dict_name in dicts:
        print("The length of dict {dict_name} is {len}".format(dict_name=dict_name, len=len(dicts[dict_name])))

    start_time = time.time()
    print("======[Replace with dict ing...]======")
    # 3. replace
    with open(os.path.join(data_path, "removed_bpe_file.src"), 'r',encoding='utf-8') as src_file_read, \
            open(os.path.join(data_path, f"expanded_{prefix}.src"), 'w+',encoding='utf-8') as src_file_write, \
            open(os.path.join(data_path, f"{prefix}.tgt"), 'r',encoding='utf-8') as tgt_file_read, \
            open(os.path.join(data_path, f"expanded_{prefix}.tgt"), 'w+',encoding='utf-8') as tgt_file_write, \
            open(os.path.join(data_path, "lang_indicator.src"), 'w+',encoding='utf-8') as lang_indic_write:
        total_replace, total_token = 0, 0
        # src_sent = src_file_read.readline()
        # tgt_sent = tgt_file_read.readline()
        for src_sent,tgt_sent in tqdm(zip(src_file_read.readlines(),tgt_file_read.readlines())):
        # while src_sent and tgt_sent:
            # src_sent = "<en> " + src_sent
            src_sent = src_sent.strip().split()
            lang_token = src_sent[0].replace("<","").replace(">","") # <de> -> de
            sent = src_sent[1:]  # remove language token

            replaced_sents, replace_cnt, sent_token = replace_sent(sent, lang_token, dicts)
            total_replace += replace_cnt
            total_token += sent_token
            # replaced_sents = [sent for sent in replaced_sents]
            # replaced_sents = [" ".join(sent) + "\n" for sent in replaced_sents] # 不带lang token，后面bpe后再paste上去
            replaced_sents = [f"<{lang_token}> "+" ".join(sent) + "\n" for sent in replaced_sents]

            # write every sent so to save memory
            for r_sent in replaced_sents:
                src_file_write.write(r_sent)

            for _ in range(len(replaced_sents)):
                tgt_file_write.write(tgt_sent)
                lang_indic_write.write(src_sent[0]+"\n")

            # src_sent = src_file_read.readline()
            # tgt_sent = tgt_file_read.readline()

    print("======[Replaced with dict Finished]======")
    print("Done in {} seconds".format(time.time() - start_time))

    print("Total Tokens(with repeated times) is {total_token}, with {replaced_token} replaced.\n"
          "With a proportion of {proportion}% \n"
          "The repeated times are set to {num_repeat}"
          .format(total_token=total_token, replaced_token=total_replace, num_repeat=args.num_repeat,
                  proportion=total_replace / total_token * 100))

    # os.remove(os.path.join(data_path, 'removed_bpe_file.src'))
    os.system("rm {}".format(os.path.join(data_path, 'removed_bpe_file.src')))
