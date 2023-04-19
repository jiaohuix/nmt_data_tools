# TextPruner

**[TextPruner](https://github.com/airaria/TextPruner)**是由HFL开发的用于预训练语言模型的模型裁剪的工具包，可以通过词表裁剪、结构裁剪来减少冗余神经元，加快模型训练推理速度。（用于裁剪transformers的模型）

本节记录下用TextPruner对mbert进行词表裁剪，保留2种语言以适应双向翻译任务。

## 1.安装

pip:

```shell
pip install textpruner
```

源码：

```shell
git clone https://github.com/airaria/TextPruner.git
pip install ./textpruner
```



## 2.准备数据

获取iwslt数据(160k)，并取出moses

```shell
bash nmt_data_tools/examples/data_scripts/prepare-iwslt14.sh 
# 处理好的德英平行语料写入iwslt14.tokenized.de-en/
```

去除bpe和moses：

```shell
# <lang> <infolder>  <outfolder>
bash nmt_data_tools/examples/data_scripts/demoses.sh de  iwslt14.tokenized.de-en de_en_raw 
bash nmt_data_tools/examples/data_scripts/demoses.sh en  iwslt14.tokenized.de-en de_en_raw 
```

以如下方式合并德英语料：

1. 合并train、valid、test
2. 对德英语料分别随机拼接两句构造长句，如text1[sep]text2, 并与原始的短句混合，从而让bert适应不同句长的处理。（待测试效果）**（可选）**
3. 以de, en, de[sep]en, en[sep]de的方式组合德英两语料。（待测试效果）**（可选）**

```shell
# 1.合并语料(2n=348544)
cat de_en_raw/*.de  > de_en_raw/all.de
cat de_en_raw/*.en  > de_en_raw/all.en
cat de_en_raw/all.de de_en_raw/all.en > de_en_raw/all
```

2-3： 构造长句、拼接德英（**可选**,8n= 1394176，用于mlm时添加多样性）：

```shell
# 2.合并句长1、2的单语语料 (2N)
# <src> <tgt> <infolder> <outfolder> <prefix=train>(opt) <k=2>(opt) 
bash nmt_data_tools/examples/data_scripts/mergek.sh de_en_raw de_en_res2 all 1

# 3.合并德英语料 (2N*4)
mkdir datasets
cat de_en_res2/all.de de_en_res2/all.en > de_en_res2/all
# 合并de[sep]en
bash nmt_data_tools/examples/data_scripts/paste_by_sep.sh de_en_res2/all.de de_en_res2/all.en de_en_res2/deen [SEP]
# 合并 en[sep]de
bash nmt_data_tools/examples/data_scripts/paste_by_sep.sh de_en_res2/all.en de_en_res2/all.de de_en_res2/ende [SEP]

cat de_en_res2/deen de_en_res2/ende >> de_en_res2/all
```



## 3.词表裁剪

对bert-base-multilingual-cased，裁剪词表。

```shell
cfgs=TextPruner/examples/configurations/
ptm=bert-base-multilingual-cased
data=de_en_raw/all 

textpruner-cli  \
  --pruning_mode vocabulary \
  --configurations $cfgs/vc.json $cfgs/gc.json \
  --model_class AutoModel \
  --tokenizer_class AutoTokenizer \
  --model_path $ptm \
  --vocabulary $data
```

[![p9FtafP.png](https://s1.ax1x.com/2023/04/19/p9FtafP.png)](https://imgse.com/i/p9FtafP)

## 4.上传huggingface



```shell
sudo apt-get install git-lfs

#transformers-cli login
huggingface-cli login
#transformers-cli repo create your-model-name # 手动创建个repo
git clone https://huggingface.co/username/your-model-name
cd your-model-name
git lfs install
git config --global user.email "email@example.com"
git add .
git commit -m "Initial commit"
git push https://username:password@huggingface.co/username/your-model-name
```

如使用git lfs install遇到错误：[git: 'lfs' is not a git command unclear](https://stackoverflow.com/questions/48734119/git-lfs-is-not-a-git-command-unclear)

```shell
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
```

