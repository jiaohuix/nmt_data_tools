# topk相似样本搜索

前言：为了方便从语料库中搜索与某个小型语料相近的样本，使用LASER编码成语义向量然后用faiss进行向量查找。

## 1 安装环境

faiss针对高维空间中的海量数据（稠密向量），提供了高效且可靠的相似性聚类和检索方法，可支持十亿级别向量的搜索，是目前最为成熟的近似近邻搜索库。

```shell
git clone https://github.com/MiuGod0126/nmt_data_tools.git
export TOOLS=$PWD/nmt_data_tools/
cd nmt_data_tools

pip install faiss-gpu transliterate fairseq==0.10.0 tqdm -i https://pypi.tuna.tsinghua.edu.cn/simple
```

​		LASER是语言无关的句子编码器，能将各种语言的句子编码成统一空间中的句向量。目前有三个版本，其中LASER1和2的都是93种语言的通用编码器，而NLLB最新发布的LASER3扩展了更多语言，这些扩展的语言各自有一个编码器。

```shell
# 1 下载代码
git clone https://github.com/facebookresearch/LASER.git
export LASER=${PWD}/LASER/
cp search/scripts/download_models.sh LASER/nllb/
cp search/scripts/install_external_tools.sh LASER/

# 2 下载权重(耗时较久，可另开终端进入下一步，重开终端还要设置LASER环境变量)
mkdir LASER/models/  && cd LASER/models/
bash ../nllb/download_models.sh    wol_Latn 
cd ..
# 3 安装依赖 (耗时更久)
bash install_external_tools.sh 
# 4 设置embed的模型路径
sed -i "s|model_dir=\"\"|model_dir=${LASER}/models|g" embed.sh
```

注意：

1. download_models.sh 默认下载LASER2和LASER3的全部权重特别耗时，而LASER2编码器是通用的，本教程只用laser2。（wol_Latn是为了只下载这种语言的laser3权重哈哈）

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

```shell
bash tasks/embed/embed.sh file xx.bin
```



## 3 向量查找

```shell
python search/laser/laser_search.py -d valid.en.bin -q test.en.bin -o test.en  -k 2 -b 512  --index FLAT --nlist 100

```

## 4 文本抽取

```shell
python search/laser/extract_text_by_idx.py infile scorefile resfile
```



## 5 pipeline

