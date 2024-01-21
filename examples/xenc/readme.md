## 领域语料过滤

使用XenC可以同时使用源、目标端的领域内外交叉熵差来过滤与领域相近的语料。



## 1 安装xenc

```shell
apt-get update
apt-get install -y libboost-all-dev libbz2-dev cmake
#git clone https://github.com/antho-rousseau/XenC.git
git clone https://gitee.com/ziwang757/XenC.git
cd XenC
cmake . && make 
# find / -name boost
# cmake . -DBOOST=/usr/include/boost/

# 起别名
cd ..
alias xenc=$PWD/XenC/XenC
```

## 2 准备语料

下面的语料是讯飞翻译比赛的数据，包含新闻平行语料2m，医疗平行语料5w。

```
pip install lxml jieba zhconv 
git clone https://gitee.com/miugod/nmt_data_tools.git
```

```shell
bash nmt_data_tools/examples/xenc/down_zhen.sh 
```

## 3 领域数据过滤

用xenc获取打分的结果

```shell
# 1 mono
xenc -s zh --mono -i data/medical.tok.zh  -o  data/news.tok.zh -m 2  --mem 25%  --threads 8 --temp ./tmp
# 不用-t必须用mono，输出如下：
# news.zh.mode2.scored.gz  
# news.zh.mode2.sorted.gz 
# scored的是顺序打分结果；sorted是分数从小到大排序，越小越相关。
# 10 threads 2m7.547s (2m * 5w)

# 2 bi
xenc -s zh -t en -i  data/medical.tok.zh  -o  data/news.tok.zh --in-ttext   data/medical.en   --out-ttext  data/news.en  --mem 25%  -m 3 --threads 40  --temp ./tmp

# news.zh-en.mode3.scored.gz 
# news.zh-en.mode3.sorted

```

解压：

```
gunzip news.zh-en.mode3.scored.gz
gunzip news.zh-en.mode3.sorted.gz
head  news.zh-en.mode3.sorted
```

重排：

对原始文件重排序，避免分词还原后与原始文件不同。

```
cut -f 1 news.zh-en.mode3.scored > score.zhen
cp nmt_data_tools/examples/xenc/rank* .

python rank.py data/news.zh data/news.sorted.zh score.zhen 0
python rank.py data/news.en data/news.sorted.en score.zhen 0

# 或者
# bash rank_all.sh zh en data/news score.zhen 0
# order=0 (小到大排序)
```



## 报错：

error: ISO C++17 does not allow dynamic exception specifications

```shell
sed -i "s/throw(SpecialWordMissingException)//g" include/kenlm/lm/vocab.hh 
sed -i "s/throw(SpecialWordMissingException)//g" src/kenlm/lm/vocab.cc
```

