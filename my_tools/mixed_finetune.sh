#4/24 对spoken数据添加tag

# params
SRC=zh
TGT=en
train_half_size=50000
dev_half_size=956
folder=mixed
out_train_prefix=train.bpe
out_dev_prefix=dev.zh-en.dev
in_train_prefix=asr.bpe
in_dev_prefix=dev.bpe

# subsample out-domain dev （do not overlap with train!）
python my_tools/train_dev_split.py $SRC $TGT ${folder}/${out_train_prefix}  ${folder}/out_tmp_dev $dev_half_size # take dev as out-domain dev
# subsample out-domain train
python my_tools/train_dev_split.py $SRC $TGT ${folder}/out_tmp_dev/train  ${folder}/out_tmp_train $train_half_size # take dev as out-domain train
# upsample in-domain train
python my_tools/upsample.py $SRC $TGT ${folder}/${in_train_prefix}  ${folder}/in_tmp_train $train_half_size

# add <news> <spoken> tag  (only src,and ccmt not tag)
#python my_tools/append_tag.py ${folder}/out_tmp_train/dev.$SRC ${folder}/out_tmp_train/dev.tag.$SRC  news
python my_tools/prepend_tag.py ${folder}/in_tmp_train/upsample.$SRC ${folder}/in_tmp_train/upsample.tag.$SRC  BSTC # train asr src
#python my_tools/prepend_tag.py ${folder}/$in_dev_prefix.$SRC  ${folder}/$in_dev_prefix.tag.$SRC  BSTC # dev asr src


# merge train
if [ ! -e ${folder}/out ];then
  mkdir ${folder}/out
fi
cat ${folder}/out_tmp_train/dev.$SRC  ${folder}/in_tmp_train/upsample.tag.$SRC > ${folder}/out/train.tmp.$SRC
cat ${folder}/out_tmp_train/dev.$TGT  ${folder}/in_tmp_train/upsample.$TGT > ${folder}/out/train.$TGT

# merge dev
#cat ${folder}/out_tmp_dev/dev.$SRC ${folder}/$in_dev_prefix.tag.$SRC  > ${folder}/out/dev.tmp.$SRC # dev has tag
cat ${folder}/out_tmp_dev/dev.$SRC ${folder}/$in_dev_prefix.$SRC  > ${folder}/out/dev.tmp.$SRC  # dev no tag
cat ${folder}/out_tmp_dev/dev.$TGT  ${folder}/$in_dev_prefix.$TGT > ${folder}/out/dev.$TGT

# normalize chinese punc
python my_tools/normalize_punc_cn.py ${folder}/out/train.tmp.$SRC ${folder}/out/train.$SRC
python my_tools/normalize_punc_cn.py ${folder}/out/dev.tmp.$SRC ${folder}/out/dev.$SRC

# remove folder
rm ${folder}/out/train.tmp.$SRC && rm ${folder}/out/dev.tmp.$SRC
rm -r ${folder}/in_tmp_train && rm -r ${folder}/out_tmp_train && rm -r ${folder}/out_tmp_dev
echo "done!"