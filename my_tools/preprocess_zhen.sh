#!/bin/sh
# this sample script preprocesses a sample corpus, including tokenization,
# truecasing, and subword segmentation.
# for application to a different language pair,
# change source and target prefix, optionally the number of BPE operations,
# and the file names (currently, data/corpus and data/newsdev2016 are being processed)

# in the tokenization step, you will want to remove Romanian-specific normalization / diacritic removal,
# and you may want to add your own.
# also, you may want to learn BPE segmentations separately for each language,
# especially if they differ in their alphabet

# suffix of source language files
SRC=zh

# suffix of target language files
TRG=en

# number of merge operations. Network vocabulary should be slightly larger (to include characters),
# or smaller if the operations are learned on the joint vocabulary
src_bpe_operations=32000
tgt_bpe_operations=32000
# length filter
lower=1
upper=250
lengRatio=2.5
# lang id ratio
threshold=0.3

# cnpmjs.or 
# path to moses decoder: https://github.com/moses-smt/mosesdecoder.git
if [ ! -d mosesdecoder ];then
  git clone https://github.com/moses-smt/mosesdecoder.git
fi
mosesdecoder=./mosesdecoder

# path to subword segmentation scripts: https://github.com/rsennrich/subword-nmt.git
if [ ! -d subword-nmt ];then
  git clone https://github.com/rsennrich/subword-nmt.git
fi
subword_nmt=./subword-nmt/subword_nmt

# path to nematus ( https://www.github.com/rsennrich/nematus.git )
if [ ! -d nematus ];then
  git clone https://github.com/EdinburghNLP/nematus.git
fi
nematus=./nematus

# tokenize
for prefix in train multi asr dev.$SRC-$TRG dev.$TRG-$SRC
 do
   echo "punctuation and tokenize src"
   # romanian preprocess
   cat data/$prefix.$SRC | \
   $mosesdecoder/scripts/tokenizer/normalize-punctuation.perl -l $SRC | \
   $mosesdecoder/scripts/tokenizer/tokenizer.perl -a -l $SRC > data/$prefix.tok.$SRC

   echo "punctuation and tokenize tgt"
   cat data/$prefix.$TRG | \
   $mosesdecoder/scripts/tokenizer/normalize-punctuation.perl -l $TRG | \
   $mosesdecoder/scripts/tokenizer/tokenizer.perl -a -l $TRG > data/$prefix.tok.$TRG

 done
#tokenize mono
cat data/mono.$SRC | \
   $mosesdecoder/scripts/tokenizer/normalize-punctuation.perl -l $SRC | \
   $mosesdecoder/scripts/tokenizer/tokenizer.perl -a -l $SRC > data/mono.tok.$SRC


raw_lines=$(cat data/train.tok.$SRC | wc -l )
echo "raw lines: $raw_lines"

# clean empty and long sentences, and sentences with high source-target ratio (training corpus only)
$mosesdecoder/scripts/training/clean-corpus-n.perl -ratio $lengRatio data/train.tok $SRC $TRG data/train.tok.clean $lower $upper
length_filt_lines=$(cat data/train.tok.clean.$SRC | wc -l )
echo "[Length filter result]: Input sentences: $raw_lines  Output sentences:  $length_filt_lines !!!"

## train truecaser,truecase则会学习训练数据，判断句子中的名字、地点等，选择合适的大小写形式，提升翻译时候的准确性,中文一般不用
if [ ! -d model ];then
  mkdir model
fi
#$mosesdecoder/scripts/recaser/train-truecaser.perl -corpus data/train.tok.clean.$SRC -model model/truecase-model.$SRC
$mosesdecoder/scripts/recaser/train-truecaser.perl -corpus data/train.tok.clean.$TRG -model model/truecase-model.$TRG

# apply truecaser (cleaned training corpus)
for prefix in train
 do
   mv data/$prefix.tok.clean.$SRC data/$prefix.tc.$SRC
#  $mosesdecoder/scripts/recaser/truecase.perl -model model/truecase-model.$SRC < data/$prefix.tok.clean.$SRC > data/$prefix.tc.$SRC
  $mosesdecoder/scripts/recaser/truecase.perl -model model/truecase-model.$TRG < data/$prefix.tok.clean.$TRG > data/$prefix.tc.$TRG

 done
mv data/mono.tok.$SRC data/mono.tc.$SRC
# apply truecaser (dev/test files)
for prefix in multi asr dev.$SRC-$TRG dev.$TRG-$SRC
 do
   mv data/$prefix.tok.$SRC data/$prefix.tc.$SRC
#  $mosesdecoder/scripts/recaser/truecase.perl -model model/truecase-model.$SRC < data/$prefix.tok.$SRC > data/$prefix.tc.$SRC
  $mosesdecoder/scripts/recaser/truecase.perl -model model/truecase-model.$TRG < data/$prefix.tok.$TRG > data/$prefix.tc.$TRG
done

tc_lines=$(cat data/train.tc.$SRC | wc -l )
echo "[Truecaser result]: Input sentences: $length_filt_lines  Output sentences:   $tc_lines!!!" #不变的！

# lang id filter，只过滤train和mono
if [ ! -e lid.176.bin ];then
  wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
fi
mv data/train.tc.$SRC data/train.tc.tmp.$SRC
mv data/train.tc.$TRG data/train.tc.tmp.$TRG
python ./my_tools/data_filter.py --src-lang $SRC --tgt-lang $TRG --in-prefix data/train.tc.tmp --out-prefix data/train.tc --threshold $threshold
rm data/train.tc.tmp.$SRC && rm data/train.tc.tmp.$TRG
lang_filt_lines=$(cat data/train.tc.$SRC | wc -l )
echo "[lang_filt result]: Input sentences: $tc_lines  Output sentences:   $lang_filt_lines!!!"
# filt mono
mv data/mono.tc.$SRC data/mono.tc.tmp.$SRC
python ./my_tools/mono_filter.py --lang $SRC  --in-prefix data/mono.tc.tmp --out-prefix data/mono.tc --threshold 0.7
rm data/mono.tc.tmp.$SRC


echo "learn bpe"
## train BPE, do not joint source and target bpe (train multi asr+mono)
cat data/train.tc.$SRC data/multi.tc.$SRC data/asr.tc.$SRC data/mono.tc.$SRC | $subword_nmt/learn_bpe.py -s $src_bpe_operations > model/$SRC.bpe
cat data/train.tc.$TRG data/multi.tc.$TRG data/asr.tc.$TRG | $subword_nmt/learn_bpe.py -s $tgt_bpe_operations > model/$TRG.bpe

# apply BPE
echo "apply BPE"
for prefix in train multi asr dev.$SRC-$TRG dev.$TRG-$SRC
 do
  $subword_nmt/apply_bpe.py -c model/$SRC.bpe < data/$prefix.tc.$SRC > data/$prefix.bpe.$SRC
  $subword_nmt/apply_bpe.py -c model/$TRG.bpe < data/$prefix.tc.$TRG > data/$prefix.bpe.$TRG
 done
$subword_nmt/apply_bpe.py -c model/$SRC.bpe < data/mono.tc.$SRC > data/mono.bpe.$SRC

# build network dictionary
echo "build network dictionary"
cat data/train.bpe.$SRC data/multi.bpe.$SRC data/asr.bpe.$SRC data/mono.bpe.$SRC > data/tmp.$SRC
cat data/train.bpe.$TRG data/multi.bpe.$TRG data/asr.bpe.$TRG  > data/tmp.$TRG
python $nematus/data/build_dictionary.py data/tmp.$SRC data/tmp.$TRG
rm data/tmp.$SRC && rm data/tmp.$TRG

## build paddle vocab
#python my_tools/json2vocab.py $SRC data
#python my_tools/json2vocab.py $TRG data
#
## build fairseq dict
#python my_tools/vocab2dict.py $SRC data
#python my_tools/vocab2dict.py $TRG data
#
## remove tmp file and move result file
#result=data/$SRC${TRG}_bpe
#if [ ! -d $result ];then
#  mkdir -p $result
#fi
#
#for prefix in train multi dev.$SRC-$TRG dev.$TRG-$SRC
#  do
#    rm data/$prefix.tok.$SRC && rm data/$prefix.tok.$TRG
#    rm data/$prefix.tc.$SRC && rm data/$prefix.tc.$TRG
#    mv data/$prefix.bpe.$SRC $result && mv data/$prefix.bpe.$TRG $result
#  done
#rm data/train.tok.clean.$SRC && rm data/train.tok.clean.$TRG
#mv data/vocab.$SRC $result && mv data/vocab.$TRG $result
#mv data/dict.$SRC.txt $result && mv data/dict.$TRG.txt $result
#
#echo "Done!"
