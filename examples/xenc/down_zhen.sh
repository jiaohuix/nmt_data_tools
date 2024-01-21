outdir=data
echo "----- step1: download and extract raw data. -----"
URL="https://ai-contest-static.xfyun.cn/2022/%E6%95%B0%E6%8D%AE%E9%9B%86/%E9%A2%86%E5%9F%9F%E8%BF%81%E7%A7%BB%E6%9C%BA%E5%99%A8%E7%BF%BB%E8%AF%91%E6%8C%91%E6%88%98%E8%B5%9B2.0%E6%95%B0%E6%8D%AE%E9%9B%86.zip"
if [ ! -e domain.zip ];then
  wget -O domain.zip $URL
fi

unzip domain.zip -d domain

# cut zh
mkdir $outdir
cut -f 1 domain/train/bilingual > $outdir/news.zh
cut -f 2 domain/train/bilingual > $outdir/news.en
cut -f 1 domain/train/zh2en-medical > $outdir/medical.zh
cut -f 2 domain/train/zh2en-medical > $outdir/medical.en


python nmt_data_tools/my_tools/cut_multi.py $outdir/news.zh $outdir/news.tok.zh 10 zh
python nmt_data_tools/my_tools/cut_multi.py $outdir/medical.zh $outdir/medical.tok.zh 10 zh
