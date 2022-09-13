'''
Char级别ngram模型，防止出现OOV的词组.
输入的句子不需要分词！

TODO: 用新语料更新词表，并加大新语料生僻词的频率！
'''
import os
import re
# import jieba
import math
from tqdm import tqdm
from collections import Counter,OrderedDict
import paddle

class nGramChar(object):
    '''
    参考：https://www.jeddd.com/article/python-ngram-language-prediction.html
    '''
    def __init__(self,n_gram=3):
        self.n_gram = n_gram
        self.eps = 1e-9
        self.vocab  = None
        self.grams = None

    def sentence_logprob(self,sentence):
        # sentence = jieba.lcut(sentence)
        sentence = list("".join(sentence.strip().split()))
        prob = 0  # 初始化句子概率
        prob_ls = []
        ngrams = list(zip(*[sentence[i:] for i in range(self.n_gram)]))  # 将句子处理成n-gram的列表
        for ngram in ngrams:
            # 累加每个n-gram的对数概率，并使用加eps法进行数据平滑
            p_n = self.grams["ngrams_counter"][ngram] / len(self.grams["ngrams_counter"])
            # p_n = self.grams["ngrams_counter"][ngram]
            prefix_gram = (ngram[0], ngram[1])
            p_prev = self.grams["prefix_counter"][prefix_gram] / len(self.grams["prefix_counter"])
            # p_prev = self.grams["prefix_counter"][prefix_gram]
            prob_i = self.eps + p_n / (self.eps + p_prev)
            prob += math.log(prob_i)
            prob_ls.append(math.log(prob_i))

        avg_score = round(prob/len(ngrams),4)
        info = [f"avg: {avg_score}"] + [f"{char}: {score:.2f}" for char,score in zip(sentence,prob_ls)]
        print(info)
        return avg_score


    def update_model(self,path):
        """ use new text update model, 主要是一些生僻OOV的词，需要添加到词表，并增加概率"""
        pass

    def save_model(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
        state = OrderedDict()
        state["vocab"] =  self.vocab
        state["grams"] =  self.grams
        save_path = os.path.join(path,"model.ngram")
        paddle.save(state,save_path)
        print(f"save state to {save_path}.")


    def load_model(self,path):
        save_path = os.path.join(path, "model.ngram")
        state  = paddle.load(save_path)
        self.vocab = state["vocab"]
        self.grams = state["grams"]
        print(f"load state from {save_path}.")

    def build_vocab(self,sents):
        ''' char level vocab'''
        char_count = dict()
        # sents = self.read_sentence(self.text_file)
        for sent in sents:
            sent = "".join(sent.strip().split()) # remove space
            for char in sent:
                char_count[char] = char_count.get(char,0) + 1

        # sort {"token":id}
        char_count = sorted(char_count.items(),key=lambda x:x[1],reverse=True)
        vocab=OrderedDict()
        # TODO: add unk bos eos, token2id,id2token
        for idx,(char,freq) in enumerate(char_count):
            vocab[char]=idx
        return vocab

    def train_ngram(self,text_file):
        sents = self.read_sentence(text_file)
        print("training ngram model...")
        # vocab
        self.vocab = self.build_vocab(sents)

        # ngrma
        ngrams_list = []  # n元组（分子）
        prefix_list = []  # n-1元组（分母）
        for sent in tqdm(sents):
            # sent = sent.strip().split()
            sent = list("".join(sent.strip().split()))
            ngrams = list(zip(*[sent[i:] for i in range(self.n_gram)]))   # 一个句子中n-gram元组的列表
            prefix = list(zip(*[sent[i:] for i in range(self.n_gram-1)])) # 历史前缀元组的列表
            ngrams_list += ngrams
            prefix_list += prefix
        ngrams_counter = Counter(ngrams_list)
        prefix_counter = Counter(prefix_list)

        grams = {"ngrams_counter":ngrams_counter,"prefix_counter":prefix_counter}
        self.grams = grams
        print("train ngram model over.")

    def read_sentence(self,file):
        with open(file, "r", encoding='utf-8') as f:
            print("reading text file...")
            res = []
            for line in tqdm(f.readlines()):
                line = line.strip()
                # line = " ".join(jieba.lcut(line.strip()))
                content = re.split('，|。|；|？|！|：|\n', line)
                content = list(filter(None, content))
                res.extend(content)
        return res


if __name__ == '__main__':
    model = nGramChar(n_gram=3)
    # train model
    # model.train_ngram(text_file="cnews/cnews.test.txt")
    # model.save_model(path=".")
    # load model
    model.load_model(path="./")
    # model.train_ngram(text_file="cnews/cnews.train.txt")
    # model.train_ngram(text_file="cnews/train.cut.txt")
    # model.load_model(path=".")
    # predict
    s1 = '他似乎总是缺乏一位掌门人应有的清晰思路和价值判断'
    s2 = '他似夫总似缺乏一位掌门人应有的清晰思路和价紫判断'

    # s1 = '被送到医院后确认死亡'
    # s2 = '破送到医院后确认死亡'
    # s1 = "阿凌带看平啊"
    # s2 = "阿凌带着伞啊"
    prob1 = model.sentence_logprob(sentence=s1)
    prob2 = model.sentence_logprob(sentence=s2)
    print(f"Sentence: {s1}, Score: {prob1}")
    print(f"Sentence: {s2}, Score: {prob2}")
    #
    # prob3 = model.sentence_logprob(sentence=s3)
    # prob4 = model.sentence_logprob(sentence=s4)
    # print(f"{s3}: {prob3}")
    # print(f"{s4}: {prob4}")

    # model.save_model(path=".")

    '''
    reading text file...
    100%|██████████| 10000/10000 [00:00<00:00, 45872.18it/s]
    training ngram model...
    100%|██████████| 631312/631312 [00:03<00:00, 158823.98it/s]
    train ngram model over.
    save state to .\model.ngram.
    ['avg: -10.397', '他: -20.72', '似: -20.72', '夫: -20.72', '总: -20.72', '似: -20.72', '缺: -4.93', '乏: -4.11', '一: -8.69', '位: -1.40', '掌: -1.80', '门: -5.44', '人: -4.73', '应: -2.20', '有: -8.45', '的: -2.78', '清: -7.58', '晰: -1.40', '思: -4.35', '路: -5.09', '和: -20.72', '价: -20.72', '紫: -20.72']
    ['avg: -4.171', '他: -1.40', '似: -6.08', '乎: -1.55', '总: -6.78', '是: -2.38', '缺: -4.93', '乏: -4.11', '一: -8.69', '位: -1.40', '掌: -1.80', '门: -5.44', '人: -4.73', '应: -2.20', '有: -8.45', '的: -2.78', '清: -7.58', '晰: -1.40', '思: -4.35', '路: -5.09', '和: -2.31', '价: -6.91', '值: -1.40']
    Sentence: 他似乎总是缺乏一位掌门人应有的清晰思路和价值判断, Score: -4.171
    Sentence: 他似夫总似缺乏一位掌门人应有的清晰思路和价紫判断, Score: -10.397
    
    Sentence: 被送到医院后确认死亡, Score: -10.2888
    Sentence: 破送到医院后确认死亡, Score: -12.5591
    
    # OOV!!!
    ['avg: -20.7233', '阿: -20.72', '凌: -20.72', '带: -20.72', '看: -20.72']
    ['avg: -20.7233', '阿: -20.72', '凌: -20.72', '带: -20.72', '着: -20.72']
    Sentence: 阿凌带看平啊, Score: -20.7233
    Sentence: 阿凌带着伞啊, Score: -20.7233
    
    '''