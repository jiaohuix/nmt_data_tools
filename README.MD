## 角灰的文本处理工具

下载并安装依赖：

```shell
git clone https://github.com/MiuGod0126/nmt_data_tools.git
cd nmt_data_tools
pip install -r requirements.txt
```

### 1.中文jieba**分词**，与⭐多进程分词

**新增：单个py脚本支持中文zh、泰文th的多进程分词。   22/8/12**

```
python my_tools/cut_multi.py <infile> <outfile> <workers> <lang>(zh/th)
```

以前的，可以不用看了。

```shell
# 1.单进程
python my_tools/cut.py src_file tgt_file
# 2.多进程
workers=4
bash my_tools/cut.sh  $workers src_file tgt_file

# 3.example:
bash my_tools/cut.sh 4 data/train.zh data/train.tok.zh
# result: 啊额最后一站了，然后回到了大本营北京。=>啊 额 最后 一站 了 ， 然后 回到 了 大本营 北京 。
```

新增泰语分分词：

```shell
bash my_tools/cut_th.sh  $workers src_file tgt_file
```



### 2.**词表转换**

json->vocab(paddle)->dict(fairseq)

**新增：1. json2dict，不再需要从vocab中转，且能保留词频信息。 2.json2vocab和json2dict加入min_freq，参数，支持按照频率过滤词表  22/8/12**

```shell
# 1.json 转 paddle vocab
#python my_tools/json2vocab.py $infile $outfile $min_freq(optional)
python my_tools/json2vocab.py data/train.bpe.zh.json data/vocab.zh


# 2.json 转 fairseq dict
#python my_tools/json2dict.py $infile $outfile $min_freq(optional)


# 3.paddle vocab 转 fairseq dict
# python my_tools/vocab2dict.py $infile $outfile $min_freq(optional)
python my_tools/vocab2dict.py data/vocab.zh data/dict.zh.txt

# 4.fairseq dict 转  paddle vocab
# python my_tools/dict2vocab.py $infile $outfile

python my_tools/dict2vocab.py data/dict.zh.txt data/vocab.zh
```

### 3.**过滤**

1.**⭐语言标识过滤**

使用fasttext

```shell
# 1.下载权重（放nmt_data_tools目录下）
wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
# 2.过滤平行语料
python ./my_tools/data_filter.py --src-lang $SRC --tgt-lang $TRG --in-prefix data/train --out-prefix data/trainlang --threshold 0.5

# 3.example
python ./my_tools/data_filter.py --src-lang zh --tgt-lang en --in-prefix data/train --out-prefix data/trainlang --threshold 0.1
# result: lang id filter| [967/1000] samples retained, [33/1000] were deleted.

```

**2.长度过滤**

替代moses的clean-corpus，打印统计信息。

```shell
# 长度检测 (用于tokenize后，bpe前)
# python my_tools/check_pair.py <in_prefix> <SRC> <TRG>  <upper> <ratio> <write_trash>(0/1)
python my_tools/check_pair.py data/train.tok zh th  175 1.5 0
# 默认write_trash=0，只打印，不写trash；0时会把范围外的异常数据写入 <inprefix.trash.lang>

# 长度过滤 (替代moses的clean-corpus；可以使用在bpe之后，先获得词表，再按不同的参数过滤数据)
python my_tools/length_filter.py --src-lang zh --tgt-lang th --in-prefix  data/train.bpe --out-prefix data/train.clean --low 1 --up 200 --ratio 1.5 --remove-bpe --wt 
# --remove-bpe可选，开启后判断长度时删掉@@ ，不影响写入； --wt可选，效果同check_pair的write_trash
```

```shell
check 结果：
              ratio       src_len       tgt_len
count  1.503344e+06  1.503344e+06  1.503344e+06
mean   1.613559e+00  7.379560e+00  8.033880e+00
std    9.832292e-01  5.450975e+00  5.950167e+00
min    1.000000e+00  1.000000e+00  1.000000e+00
25%    1.142857e+00  4.000000e+00  5.000000e+00
50%    1.333333e+00  6.000000e+00  7.000000e+00
75%    1.714286e+00  9.000000e+00  1.000000e+01
max    8.500000e+01  5.100000e+02  5.010000e+02
84 lines len > 175, 65409 lines ratio > 3.0.
step info: {'1.5': 494654, '2': 194131, '2.5': 118475, '3': 65409}
```



### 4.批量**提取xml**和sgm

#### 4.1提取单个xml：

```shell
# 1.command:
python my_tools/process_xml.py $infile $outfolder

# 2.example:
python my_tools/process_xml.py data/xml/bgzh/val.bg-zh.bg.xml data/
# result:
#total 1000 lines.
#write to data/val.bg-zh.bg.txt success.
```

#### 4.2 ⭐提取含xml的文件夹

```
############### input ############### ：
data/xml
├── bgzh
│   ├── val.bg-zh.bg.xml
│   └── val.bg-zh.zh.xml
└── ruzh
    ├── val.ru-zh.ru.xml
    └── val.ru-zh.zh.xm
############### output ############### ：
xml_out/
├── bgzh
│   ├── val.bg-zh.bg.txt
│   └── val.bg-zh.zh.txt
└── ruzh
    ├── val.ru-zh.ru.txt
    └── val.ru-zh.zh.txt
```

```shell
# 1.command:
bash my_tools/process_xml_folder.sh <infolder> <outfolder>

# 2.example:
bash my_tools/process_xml_folder.sh data/xml/ xml_out
```

### 5.⭐写入xml：

```shell
# 1.生成xml
python my_tools/write_xml.py data/train.en data/result.xml
# 2.再在xml开头添加
<?xml version="1.0" encoding="UTF-8"?>

# input:  So this is our last stop, and we came back to our headquarter in Beijing.
# output:
<tstset setid="nestest2019" srclang="zh" trglang="en">
  <DOC docid="news" sysid="1">
    <p>
      <seg id="1">So this is our last stop, and we came back to our headquarter in Beijing.</seg>
```

### 6.流式输入处理
如：
```
大
大家
大家晚         <=========> 大家晚上好
大家晚上
大家晚上好
```

```shell
# 1.command:
python my_tools/stream_preprocess.py <infile> <outfile> <1(towhole)|2(tostream)> <lang>

# 2.example:
# 流式->整句（data/whole.zh）
python my_tools/stream_preprocess.py data/stream.zh data/whole.zh 1 zh
# 整句->流式（data/stream2.zh）
python my_tools/stream_preprocess.py data/whole.zh data/stream2.zh 2 zh
```

### 7.合并、拆分语料

#### 7.1合并

```shell
# 1.python
# python {sys.argv[0]} <infile1> <infile2> <outfile> <sep> (space/tab)
# 空格分隔
python my_tools/merge.py data/train.zh data/train.en data/outfile.txt space
# 制表符分割
python my_tools/merge.py data/train.zh data/train.en data/outfile.txt tab

# 2.shell
paste data/train.zh data/train.en > data/outfile.txt
# paste -d ' ' 空格分割不好用，默认\t
```

#### 7.2 拆分

```shell
# src
cut -f 1 data/outfile.txt > data/cut.zh
# tgt
cut -f 2 data/outfile.txt > data/cut.en
```

### 8.数据划分

划分训练和验证集

```shell
# 1.command:
python my_tools/train_dev_split.py <src-lang> <tgt-lang> <inprefix> <outfolder> <dev len>

# 2.example:
python my_tools/train_dev_split.py zh en data/train data 500
# 从train中随机取500条到data/dev.zh/en，其余的data/train.zh/en,result:
write to data\train.zh success.
write to data\train.en success.
write to data\dev.zh success.
write to data\dev.en success.
```

### 9.上、下采样

#### 9.1 上采样

```shell
# 1.command:
python my_tools/upsample.py <src-lang> <tgt-lang> <inprefix> <outfolder> <upsample len>
 
# 2.example:
python my_tools/upsample.py zh en data/train data 10000
# result:
write to data\upsample.zh success.
write to data\upsample.en success.
```

#### 9.2 下采样

直接使用8数据划分，取dev.lang作为下采样结果

### 10.打乱平行语料

```shell
# 1.command:
python my_tools/shuffle_pair.py <src_lang> <tgt_lang> <data_prefix> <out_folder>

# 2.example:
python my_tools/shuffle_pair.py zh en data/train data/
# result:
write to data/shuffle.zh success.
write to data/shuffle.en success.
```

### 11.去重

**新增： 双语去重。（无序，比有序快25%）**

```shell
# python my_tools/deduplicate_pairs.py  <in_prefix> <src_lang> <tgt_lang>  <workers>
# 会默认写到in_prefix.dedup.lang里,example:
python my_tools/deduplicate_pairs.py  data/train zh en  4
```

old：单语多文件去重 。（无序）

```shell
# 1.command:
python my_tools/deduplicate_lines.py --workers $workers files > $outfile

# 2.example:
python my_tools/deduplicate_lines.py --workers 4 data/upsample.zh > data/dedup.zh
wc data/dedup.zh
# 493   499 48302 data/dedup.zh
```

### 12.⭐翻译数据处理

以zh en为例进行数据处理：

```shell
bash preprocess.sh
```

### 13.后处理

对英文detokenize+detruecase

```shell
# bash postprocess.sh <prefix>
bash postprocess.sh data/zhen_bpe/train.bpe
```

### 14.fast_align抽取词典

```shell
# 分词
bash my_tools/cut.sh 4 data/train.zh data/train.tok.zh
bash my_tools/cut.sh 4 data/dev.zh data/dev.tok.zh
mv data/train.tok.zh data/train.zh
mv data/dev.tok.zh data/dev.zh
# 抽取词典 （data/fast_align/dict.zh-en）
bash fast_align_dict.sh
# 查看结果
head -n 10 data/fast_align/dict.zh-en
我们    we      148
的      of      142
的      the     120
这个    the     100
是      is      100
，      and     94
一个    a       84
的      in      82
我们    our     76
可以    can     74
```

目前已经可以抽取词典，后续准备添加停用词过滤，然后清洗词典，或者检测并保留些实体词，就不放在抽取词典上了。

### 15.RAS

随机对齐替换。用词典将source的词典词按一定几率替换为其他语言的同义词。

```
python my_tools/replace_word_bilingual.py --langs de;en --dict-path dic --data-path data  --prefix train --num-repeat 1 --moses-detok --replace-prob 0.3 --vocab-size 1000

tree:
/dic
	de-en.txt # de_word en_word \n (空格分隔)
/data
	train.src # <lang_id> src_text
	train.tgt  # <lang_id> tgt_text
```

python nmt_data_tools/my_tools/replace_word_bilingual.py --langs de;en --dict-path dic --data-path data --num-repeat 1 --moses-detok --replace-prob 0.3 --vocab-size 1000

**完整文档和demo参考[ras_sample](./ras_sample/README.md)**

