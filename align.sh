# 1.code
git clone https://github.com/facebookresearch/MUSE.git
cd MUSE/data

# 2.download embed
wget https://dl.fbaipublicfiles.com/arrival/vectors/wiki.multi.ar.vec
wget https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.zh.vec

# 2.download dictionary (ar/zh train/test)
wget https://dl.fbaipublicfiles.com/arrival/dictionaries/ar-en.txt
wget https://dl.fbaipublicfiles.com/arrival/dictionaries/zh-en.txt
cd ..

# 3.make zh-ar dictionary by zh-en ar-en
python ../my_tools/get_pivot_dict.py  data/zh-en.txt data/ar-en.txt
head -n 8000 data/zh-ar.txt > data/zh-ar.train.txt
tail -n +8001 data/zh-ar.txt > data/zh-ar.eval.txt

# align zh-ar in a common space
python supervised.py --src_lang zh --tgt_lang ar --src_emb data/wiki.zh.vec --tgt_embed data/wiki.multi.ar.vec --n_refinement 5 --dico_train data/zh-ar.train.txt --dico_eval data/zh-ar.eval.txt
