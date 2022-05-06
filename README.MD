## 角灰的文本处理工具

### 1.中文jieba**分词**，与⭐多进程分词

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

### 2.**词表转换**

json->vocab(paddle)->dict(fairseq)

```shell
# 1.json 转 paddle vocab
python my_tools/json2vocab.py $infile $outfile
#example:
python my_tools/json2vocab.py data/train.bpe.zh.json data/vocab.zh

# 2.paddle vocab 转 fairseq dict
python my_tools/vocab2dict.py $infile $outfile
#example:
python my_tools/vocab2dict.py data/vocab.zh data/dict.zh.txt

# 3.fairseq dict 转  paddle vocab
python my_tools/dict2vocab.py $infile $outfile
#example:
python my_tools/dict2vocab.py data/dict.zh.txt data/vocab.zh
```

### 3.**lang id过滤**

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

#### 4.2 提取含xml的文件夹



```
目录：
```



```shell
# 1.command:
bash my_tools/process_xml_folder.sh <infolder> <outfolder>

# 2.example:
bash my_tools/process_xml_folder.sh data/xml/ xml_out

#result
processing bgzh/val.bg-zh.bg.xml
total 1000 lines.
write to xml_out/bgzh\val.bg-zh.bg.txt success.
processing bgzh/val.bg-zh.zh.xml
total 1000 lines.
write to xml_out/bgzh\val.bg-zh.zh.txt success.
processing ruzh/val.ru-zh.ru.xml
total 1000 lines.
write to xml_out/ruzh\val.ru-zh.ru.txt success.
processing ruzh/val.ru-zh.zh.xml
total 1000 lines.
write to xml_out/ruzh\val.ru-zh.zh.txt success.

```

### 5.写入xml：

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
python my_tools/merge.py data/train.zh data/train.en data/outfile.txt
# 2.shell
paste data/train.zh data/train.en > data/outfile.txt
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

```shell
# 1.command:
python my_tools/deduplicate_lines.py --workers $workers files > $outfile

# 2.example:
python my_tools/deduplicate_lines.py --workers 4 data/upsample.zh > data/dedup.zh
wc data/dedup.zh
# 493   499 48302 data/dedup.zh

```

