# 使用fast_align抽取平行词典



## 1.准备

```shell
git clone https://gitee.com/miugod/nmt_data_tools.git
bash nmt_data_tools/examples/fast_align/word_extract/install.sh
```

## 2.处理数据

```shell
bash  nmt_data_tools/examples/data_scripts/prepare-iwslt14.sh 
# 去掉bpe
sed -i "s/@@ //g"  iwslt14.tokenized.de-en/train.en
sed -i "s/@@ //g"  iwslt14.tokenized.de-en/train.de
```

## 3.fast align对齐

```shell
bash nmt_data_tools/examples/fast_align/word_extract/align.sh de en iwslt14.tokenized.de-en/
# _align是对齐的id，params是词的分数
```

## 4.抽取词典

```shell
# 利用对齐文件train.sym_align，从双语句对train.de-en中抽取topk=5w的词典，输出到dict.de-en.txt
python nmt_data_tools/my_tools/extract_dict.py iwslt14.tokenized.de-en/train.de-en iwslt14.tokenized.de-en/train.sym_align dict.de-en.txt  50000
```



## 5.过滤

```shell
# 利用停用词、fasttext语言标识过滤，并去除1:m,m:1,m:n的词对
wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin

python nmt_data_tools/my_tools/dict_filter.py de en  dict.de-en.txt dict.de-en.filt.txt nmt_data_tools/data/stops/de.txt nmt_data_tools/data/stops/en.txt lid.176.bin 
```

## 6.bpe并合并

```shell
cut -f1 dict.de-en.filt.txt | subword-nmt apply-bpe -c iwslt14.tokenized.de-en/code > dict.de.bpe
cut -f2 dict.de-en.filt.txt | subword-nmt apply-bpe -c iwslt14.tokenized.de-en/code > dict.en.bpe
paste dict.de.bpe dict.en.bpe > dict.de-en.bpe.txt

#klas@@ si@@ fizieren    classi@@ fy
#klas@@ si@@ fiziert     classi@@ fied
```

2023/5/7