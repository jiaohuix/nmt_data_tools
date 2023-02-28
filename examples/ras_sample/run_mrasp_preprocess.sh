#!/bin/bash

in_folder=$1
out_folder=$2
src=$3
tgt=$4
dict_path=$5
bpe_code=$6
repeat=$7
prob=$8
vocab_size=$9
use_moses=$10
if [ $use_moses == 1 ];
  then
    use_moses="--moses-detok"
  else
    use_moses=""
fi

rm -rf $out_folder

echo "--------------------Process bidirect and monolingual data.--------------------"
bash ras_sample/preprocess_mrasp_raw.sh $in_folder $out_folder $src $tgt

echo "--------------------Process Random Align Substitute data.--------------------"
# only valid for train set
for prefix in train
  do
    python my_tools/replace_word_bilingual.py --langs ${src},${tgt} --dict-path $dict_path \
           --data-path $out_folder --prefix $prefix --num-repeat $repeat  $use_moses --replace-prob $prob \
           --vocab-size $vocab_size
    bash ras_sample/merge_raw_ras.sh  $out_folder $prefix  $bpe_code $src $tgt

done
echo "All Done."
