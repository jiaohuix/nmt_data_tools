# 构建mRASP数据

## 0.依赖

```
cd nmt_data_tools
pip install -r requirements.txt
git clone https://github.com/moses-smt/mosesdecoder.git
```



## 1.双向数据+单语，得到raw

- 输入数据是已经tokenize、clean、bpe处理好的。
- 默认将平行语料(src,tgt)得到（src,tgt）(tgt,src) (src,src) (tgt,tgt)这样四倍的预训练数据，并且句子开头加上language token，如<de>。 
- 对于test，仅添加语言标识，不会扩充，以后也不会。
- 【TODO: 添加单语】已完成√ 将mono.src 得到(src,src), mono.tgt得到(tgt,tgt)，若无mono.lang则忽略。

```
# 数据格式
# 数据格式
de_en/
├── code # joint bpe code
├── dict
│   └── de-en.txt
├── mono.de
├── mono.en
├── test.de
├── test.en
├── train.de
├── train.en
├── valid.de
├── valid.en
├── vocab.de
└── vocab.en
```



```shell
# bash ras_sample/preprocess_mrasp_raw.sh <in_folder> <out_folder> <src> <tgt>
bash ras_sample/preprocess_mrasp_raw.sh data/de_en  data/de_en_ras de en

# de_en_ras/ test.src  test.tgt  train.src  train.tgt  valid.src  valid.tgt  vocab.src  vocab.tgt
```

## 2.抽取RAS句子

- 按照data/de_en/dict目录下形如lang1-lang2.txt的词典，对1得到的raw语料源端的句子进行随即对齐替换（RAS）,找到词典词后以prob几率用另一种语言的同义词替换，每句话替换repeat次，词典取前vocab-size个。

- 基本上vocab-size=1000能替换6%-8%的词，再放大10倍vocab-size=10000，也仅仅达到12%。

- --moses-detok若使用会把非中文的语言，按照该语言进行moses tokenize。

- 对于双语词典，参考fast-align或从MUSE下载

- [TODO]: moses、bpe完成了，还需要添加些clean的，如添加truecase，punctuation等。

```shell
# 以train为例
python my_tools/replace_word_bilingual.py --langs de,en --dict-path data/de_en/dict --data-path data/de_en_ras --prefix train --num-repeat 1 --moses-detok --replace-prob 0.3 --vocab-size 1000

# result:
Namespace(data_path='data/de_en_ras', dict_path='data/de_en/dict', langs='de,en', moses_detok=True, num_repeat=1, prefix='train', replace_prob=0.3, vocab_size=1000)
======[Remove bpe ing...]======
======[Loade Dicts ing... ]======
dict_keys(['de-en', 'en-de'])
The length of dict de-en is 1000
The length of dict en-de is 1000
======[Replace with dict ing...]======
======[Replaced with dict Finished]======
Done in 0.1346118450164795 seconds
Total Tokens(with repeated times) is 74378, with 6592 replaced.
With a proportion of 8.862835784775069%
The repeated times are set to 1
```

## 3.合并raw和ras

将第一二两步得到4X和3X的数据合并起来，约得到7倍于原先平行语料的数据。对于valid取前5000条。

```shell
# 以train为例
# bash ras_sample/merge_raw_ras.sh <in_folder> <prefix> <bpe_code_file> <src> <tgt>
bash ras_sample/merge_raw_ras.sh  data/de_en_ras train  data/de_en/code de en
```

## 4.Pipeline

一键完成数据处理。

```shell
# bash ras_sample/run_mrasp_preprocess.sh <in_folder> <out_folder> <src> <tgt> <dict_path>  <bpe_code> <repeat> <prob> <vocab_size>
bash ras_sample/run_mrasp_preprocess.sh data/de_en data/de_en_ras de en data/de_en/dict     data/de_en/code 1 0.3 1000
```

```
# tree
```



## 5.其他

1. 获取完整iwslt14_de_en数据:

   ```shell
   bash ras_sample/prepare-iwslt14.sh
   ```

2. 对含有language token的文件进行moses tokenize,支持混则多种语言。将不同语言的句子分开后tokenize,然后再合并。

   ```shell
   # bash ras_sample/moses_mix_lang.sh <prefix> <surfix> <src> <tgt> <outfile>
    bash ras_sample/moses_mix_lang.sh data/de_en_ras/valid src de en data/de_en_ras/a.txt
   ```

   