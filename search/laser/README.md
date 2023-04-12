# topk相似样本搜索

前言：为了方便从语料库中搜索与某个小型语料相近的样本，使用LASER编码成语义向量然后用faiss进行向量查找。

## 1 安装环境

faiss针对高维空间中的海量数据（稠密向量），提供了高效且可靠的相似性聚类和检索方法，可支持十亿级别向量的搜索，是目前最为成熟的近似近邻搜索库。

```shell
git clone https://github.com/jiaohuix/nmt_data_tools.git
export TOOLS=$PWD/nmt_data_tools/
cd nmt_data_tools

pip install faiss-gpu transliterate fairseq==0.10.0 tqdm -i https://pypi.tuna.tsinghua.edu.cn/simple
```

​		LASER是语言无关的句子编码器，能将各种语言的句子编码成统一空间中的句向量。目前有三个版本，其中LASER1和2的都是93种语言的通用编码器，而NLLB最新发布的LASER3扩展了更多语言，这些扩展的语言各自有一个编码器。

```shell
# 1 下载代码
git clone https://github.com/facebookresearch/LASER.git
export LASER=${PWD}/LASER/
cp search/laser/scripts/download_models.sh LASER/nllb/
cp search/laser/scripts/install_external_tools.sh LASER/

# 2 下载权重(耗时较久，可另开终端进入下一步，重开终端还要设置LASER环境变量)
mkdir LASER/models/  && cd LASER/models/
bash ../nllb/download_models.sh    wol_Latn 
cd ..
# 3 安装依赖 (耗时更久)
bash install_external_tools.sh 
# 4 设置embed的模型路径
sed -i "s|model_dir=\"\"|model_dir=${LASER}/models|g"  tasks/embed/embed.sh 
```

注意：

1. download_models.sh 默认下载LASER2和LASER3的全部权重特别耗时，而LASER2编码器是通用的，本教程只用laser2。

   - **wol_Latn**是为了下载laser3权重的子集，否则会下载全部权重，当下载到下面这条就可以停止啦：

     ```shell
     - https://dl.fbaipublicfiles.com/nllb/laser/laser3-wol_Latn.v1.pt
     ```

2. install_external_tools.sh 中第75行为moses下载大量的“nonbreaking_prefix”，耗时巨久可以注释掉，只取自己需要的即可，我改成了 ”中英德”：

   ```shell
   # 原始
   moses_non_breaking_langs=( \
       "ca" "cs" "de" "el" "en" "es" "fi" "fr" "ga" "hu" "is" \
       "it" "lt" "lv" "nl" "pl" "pt" "ro" "ru" "sk" "sl" "sv" \
       "ta" "yue" "zh" )
   # 修改
   moses_non_breaking_langs=( "zh" "en" "de" )
   ```

3. 此外，还为两个脚本添加了多进程下载，形如:

   ```shell
   for file in ${files[@]} ; do
       (
       wget  $file
       )&
   done
   wait
   ```



## 2 向量编码

以nmt_data_tools/data/train.zh为例，随机划分400条作为database，100条为query，使用laser编码：


```shell
# cmd: bash tasks/embed/embed.sh infile  out_bin_file

# 1 划分database和query
python ../my_tools/train_dev_split.py zh en ../data/train  ./ 100

# 2 分词
pip install zhconv jieba
bash ../my_tools/cut.sh 4  train.zh  train.tok.zh zh
bash ../my_tools/cut.sh 4  dev.zh  dev.tok.zh zh

# 3 编码
bash tasks/embed/embed.sh train.tok.zh  database.bin
bash tasks/embed/embed.sh  dev.tok.zh  query.bin
```

PS: 可以把源和目标语拼在一起联合编码，从而提高向量搜索的准确度。
```
# 3 编码

paste  train.tok.zh train.en  > train.all
paste  dev.tok.zh   dev.en > dev.all
bash tasks/embed/embed.sh train.all  database.bin
bash tasks/embed/embed.sh dev.all    query.bin
```

## 3 向量查找

利用faiss向量检索库，从database中找到与query最相似的100条：

```shell
python ../search/laser/laser_search.py -d  database.bin -q  query.bin -o sim  -k 2 -b 512  --index IVF --nlist 100  
# 建议使用--index IVF，从16w中搜索16w条， FLAT需要50min，IVF 3min(8core)
# 输出为： sim.dist   sim.idx， dist是k列距离；idx是k列索引
```

## 4 文本抽取

取出top1列索引，从databse中抽取文本：

```shell
#cmd :python search/laser/extract_text_by_idx.py infile scorefile resfile
cut -f1 sim.idx > sim.top1.idx
python ../search/laser/extract_text_by_idx.py train.tok.zh sim.top1.idx   dev.top1.zh
python ../search/laser/extract_text_by_idx.py train.en sim.top1.idx   dev.top1.en
```

查看前五条,原始文本：

```shell
#  head -n 5  dev.tok.zh 
1 我来 了 。
2 我们 希望 跟 我们 的 这个 合作伙伴 能够 真正 这个 携手 起来 ， 我们 培养 更 多 的 深度 学习 的 这个 工程师 ， 我们 帮助 更 多 的 创业 企业 。
3 首先 来说 的话 呢 ， 我们 实际上 整个 UNIT 是 这样 的 一个 框架 ， 就是说 我们 的 开发者 只 需要 上面 去 提供 我们 的 一些 目标 的 定制 以及 就是 训练 的 一些 数据 ， 然后 就 可以 进 到 我们 的 整个 学习 的 这样 的 一个 环节 里 。
4 就是 我 没有 叫醒 你 ， 你 突然 之间 认为 我 在 跟 你 这 这个 对 对话 ， 开始 这个 进行 语音 识别 。
5 额 用户 问 的 部分 ， 额 刚才 那个 有 两有 两个 概念 ， 不 知道 大家 注意 没有 ？
```

相似文本：

```shell
#  head -n 5  dev.top1.zh 
1 好 。
2 所以 我们 本身 在 这个 希望 能够 帮助 更 多 的 开发者 去 转型 为 深度 学习 的 这个 工程师 。
3 实际上 这 里面 实际上 就是 体现 了 一个 非常 关键 的 一个 技术 ， 就是 我们 通过 对话 ， 我们 只 需要 通过 对话 ， 然后 我们 就 可以 轻易 地去 控制 我们 的 这 这样 的 一个 就是 额 这样 的 一个 设备 ， 然后 让 它 去 执行 所有 我们 所 期望 它 去 执行 的 一些 指令 。
4 就是 你 在 小声 轻声 说话 的 时候 ， 就是 你 的 这个 声音 ， 你 的 这个 声带 没有 震动 的 时候 你 去 跟 它 喷 那个 字 ， 它 也 会 非常 好 地 给 你 识别 出来 。
5 这个 是 额 刚刚 上线 的 这个 呼叫 中心 的 语音 识别 。
```



## 5 pipeline

