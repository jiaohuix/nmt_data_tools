# fasttext词表映射

利用预训练的bert初始化翻译模型，词表没有一一对应，需要进行映射。本文以roberta-base预训练模型、iwslt14德英数据为例子，用roberta-base的词表初始化翻译的词表。

## 1.环境

```shell
git clone https://github.com/jiaohuix/nmt_data_tools.git
git clone https://github.com/facebookresearch/fastText.git
cd fastText
make
python setup.py install
pip install faiss-cpu
cd ..
```

## 2.数据

2.1 roberta词典

```shell
wget https://huggingface.co/roberta-base/resolve/main/vocab.json
python nmt_data_tools/my_tools/json2dict.py vocab.json roberta.dict.txt
cut -f1 -d" " roberta.dict.txt > dict.txt
```

2.2 iwslt14数据

```shell
bash nmt_data_tools/examples/data_scripts/prepare-iwslt14.sh
# 去掉bpe
cat iwslt14.tokenized.de-en/train.* iwslt14.tokenized.de-en/valid.* iwslt14.tokenized.de-en/test.* > iwslt14.tokenized.de-en/train 
sed -i "s/@@//g"  iwslt14.tokenized.de-en/train

```

2.3 fairseq词典

```shell
# 获取词典 dict.txt
python nmt_data_tools/my_tools/build_dictionary.py iwslt14.tokenized.de-en/train
python nmt_data_tools/my_tools/json2dict.py iwslt14.tokenized.de-en/train.json iwslt14.tokenized.de-en/dict.deen.txt

echo -e "<s>\n</s>\n<pad>\n<unk>" > iwslt14.tokenized.de-en/dict.txt
cut -f1 -d" " iwslt14.tokenized.de-en/dict.deen.txt >> iwslt14.tokenized.de-en/dict.txt
```



## 3.训练fasttext

```shell
mkdir result
./fastText/fasttext skipgram -input iwslt14.tokenized.de-en/train -output result/ende -epoch 5 -dim 100
```



## 4.编码词向量

```shell
#  <model> <dict> <outfile(xx.bin)>
python nmt_data_tools/search/embed/encode_vec.py result/ende.bin iwslt14.tokenized.de-en/dict.txt fairseq.bin

python nmt_data_tools/search/embed/encode_vec.py result/ende.bin dict.txt roberta.bin
```



## 5. 相似搜索

从roberta词表中找出fairseq词表相近的topk。

```shell
# k=3
python nmt_data_tools/search/laser/laser_search.py -d roberta.bin -q fairseq.bin -o out  -k 3 -b 512  --index FLAT --nlist 100 --dim 100

#head idx_map.json
'''
{
  "0": [
    "38312",
    "18306",
    "18751"
  ],
  "1": [
    "29112",
    "17153",
    "32766"
'''
```

将索引转为token。

```shell
# <bert_dict> <nmt_dict> <idx_map_file>
python nmt_data_tools/examples/vocab_map/idx2token_map.py iwslt14.tokenized.de-en/dict.txt dict.txt   idx_map.json
# 输出token_map.json
'''
{',': [',', '--', 'ãģ®é'],
 '.': ['.', ',', 'ItemTracker'],
 'the': ['the', 'and', 'that'],
 'in': ['in', 'ãģ®é', ','],
 'and': ['and', 'Actually', 'Ġactually'],
 'und': ['und', 'ioch', 'Nich'
'''
```



## 6.去除冗余

去掉能从roberta词表直接能找到的。

