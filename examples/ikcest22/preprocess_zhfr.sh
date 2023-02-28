#!/bin/sh

folder=$1
SRC=zh
TRG=fr

# number of merge operations. Network vocabulary should be slightly larger (to include characters),
# or smaller if the operations are learned on the joint vocabulary
src_bpe_operations=18000
tgt_bpe_operations=18000
joint_bpe=0
# length filter
lower=1
upper=256
lengRatio=2.5

valid_num=1000
split_lines=100000


if [ ! -d mosesdecoder ];then
  git clone https://github.com/moses-smt/mosesdecoder.git
fi
mosesdecoder=./mosesdecoder
SCRIPTS=mosesdecoder/scripts
NORMALIZE=$SCRIPTS/tokenizer/normalize-punctuation.perl
TOKENIZER=$SCRIPTS/tokenizer/tokenizer.perl
CLEAN=$SCRIPTS/training/clean-corpus-n.perl
TRAIN_TC=$SCRIPTS/recaser/train-truecaser.perl
TC=$SCRIPTS/recaser/truecase.perl


# train valid split(ikcest),merge ikcest and un
python my_tools/train_dev_split.py $SRC $TRG $folder/train.ikcest $folder/ $valid_num # train.lang/ dev.lang
mv $folder/dev.$SRC  $folder/valid.$SRC && mv $folder/dev.$TRG  $folder/valid.$TRG
cat $folder/train.un.$SRC  >> $folder/train.$SRC
cat $folder/train.un.$TRG  >> $folder/train.$TRG

raw_lines=$(cat $folder/train.$SRC | wc -l )
echo "raw lines: $raw_lines"

# tokenize

echo "--------------------- tokenize ---------------------"
for prefix in train valid  test.${SRC}_${TRG} test.${TRG}_${SRC} valid.un test.un
  do
    if [ -e $folder/$prefix.$SRC ];then
       echo "tokenize $prefix.$SRC"
       bash my_tools/cut.sh 4 $folder/$prefix.$SRC  $folder/$prefix.tok.$SRC # jieba分词
    fi

    if [ -e $folder/$prefix.$TRG ];then

         cat $folder/$prefix.$TRG | \
         perl $NORMALIZE -l $TRG | \
         perl $TOKENIZER -threads 8 -a -l $TRG > $folder/$prefix.tok.$TRG
    fi
  done

# deduplicate
#echo  "-------------- deduplicate --------------"
#wc $folder/train.$SRC
#paste  $folder/train.$SRC  $folder/train.$TRG > tmp.txt
#python my_tools/deduplicate_lines.py --workers 4 tmp.txt > tmp.dedup.txt
#
#cut -f 1 tmp.dedup.txt > $folder/train.dedup.$SRC
#cut -f 2 tmp.dedup.txt > $folder/train.dedup.$TRG
#
#rm tmp.txt tmp.dedup.txt
#wc $folder/train.dedup.$SRC
#

# clean empty and long sentences, and sentences with high source-target ratio (training corpus only)
#perl $CLEAN -ratio $lengRatio $folder/train.tok $SRC $TRG $folder/train.clean $lower $upper
#length_filt_lines=$(cat $folder/train.clean.$SRC | wc -l )
#echo "--------------[Length filter result]: [$length_filt_lines/$raw_lines]. --------------"

# do length filter after bpe, check statistic info first
python my_tools/check_pair.py $folder/train.tok $SRC $TRG  $upper $lengRatio 0
mv $folder/train.tok.$SRC $folder/train.clean.$SRC && mv $folder/train.tok.$TRG $folder/train.clean.$TRG


## train truecaser,truecase则会学习训练数据，判断句子中的名字、地点等，选择合适的大小写形式，提升翻译时候的准确性,中文一般不用
if [ ! -d model ];then
  mkdir model
fi
perl $TRAIN_TC  -corpus $folder/train.clean.$TRG -model model/truecase-model.$TRG

# apply truecaser (cleaned training corpus)
for prefix in train
 do
  cp $folder/$prefix.clean.$SRC $folder/$prefix.tc.$SRC
  perl $TC  -model model/truecase-model.$TRG < $folder/$prefix.clean.$TRG > $folder/$prefix.tc.$TRG

 done

# apply truecaser (dev/test files)
echo "-------------- truecase --------------"
for prefix in  valid  test.${SRC}_${TRG} test.${TRG}_${SRC} valid.un test.un
 do

    if [ -e $folder/$prefix.tok.$SRC ];then
        cp $folder/$prefix.tok.$SRC $folder/$prefix.tc.$SRC
    fi

    if [ -e $folder/$prefix.tok.$TRG ];then
        perl $TC -model model/truecase-model.$TRG < $folder/$prefix.tok.$TRG > $folder/$prefix.tc.$TRG
    fi

done

tc_lines=$(cat $folder/train.tc.$SRC | wc -l )


# lang id filter，只过滤train
if [ ! -e lid.176.bin ];then
 wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
fi

python my_tools/data_filter.py --src-lang $SRC --tgt-lang $TRG --in-prefix $folder/train.tc --out-prefix $folder/train.id
lang_filt_lines=$(cat $folder/train.id.$SRC | wc -l )
echo "--------------[lang_filt result]: [$lang_filt_lines/$length_filt_lines]. --------------"
mv $folder/train.id.$SRC $folder/train.tc.$SRC
mv $folder/train.id.$TRG $folder/train.tc.$TRG


echo "--------------------- learn bpe ---------------------"
if [ ! -d model ];then
  mkdir model
fi
## train BPE, do not joint source and target bpe

cat $folder/train.tc.$SRC > $folder/tmp.$SRC
if [ -e $folder/mono.tc.$SRC ];then
  cat $folder/mono.tc.$SRC >> $folder/tmp.$SRC
fi

cat $folder/train.tc.$TRG > $folder/tmp.$TRG

if [ -e $folder/mono.tc.$TRG ];then
  cat $folder/mono.tc.$TRG >> $folder/tmp.$TRG
fi

if [ $joint_bpe == 1 ];then
  echo "--------------------- learn joint bpe ---------------------"
  cat $folder/tmp.$TRG >> $folder/tmp.$SRC
  cp $folder/tmp.$SRC $folder/tmp.$TRG
fi

wc $folder/tmp.$SRC
wc $folder/tmp.$TRG

subword-nmt learn-bpe -s $src_bpe_operations < $folder/tmp.$SRC  > model/$SRC.bpe
if [ $joint_bpe == 0 ];then
  subword-nmt learn-bpe -s $src_bpe_operations < $folder/tmp.$TRG > model/$TRG.bpe
elif [ $joint_bpe == 1 ]; then
  cp model/$SRC.bpe model/$TRG.bpe
fi

# apply BPE
echo "--------------------- apply bpe ---------------------"
for prefix in train valid  test.${SRC}_${TRG} test.${TRG}_${SRC} valid.un test.un
 do
   if [ -e $folder/$prefix.$SRC ];then
      echo "bpe $prefix.$SRC"
      subword-nmt apply-bpe -c model/$SRC.bpe < $folder/$prefix.tc.$SRC  >  $folder/$prefix.bpe.$SRC
   fi
   if [ -e $folder/$prefix.$TRG ];then
      echo "bpe $prefix.$TRG"
      subword-nmt apply-bpe -c  model/$TRG.bpe < $folder/$prefix.tc.$TRG > $folder/$prefix.bpe.$TRG
   fi
 done


#build network dictionary
echo "--------------------- build network dictionary ---------------------"
cat $folder/train.bpe.$SRC > $folder/tmp.$SRC
if [ -e $folder/mono.bpe.$SRC ];then
  cat $folder/mono.bpe.$SRC >> $folder/tmp.$SRC
fi

cat $folder/train.bpe.$TRG > $folder/tmp.$TRG
if [ -e $folder/mono.bpe.$TRG ];then
  cat $folder/mono.bpe.$TRG >> $folder/tmp.$TRG
fi

if [ $joint_bpe == 1 ];then
    echo "------- build joint vocab ------- "
  cat $folder/tmp.$TRG >> $folder/tmp.$SRC
  # cp $folder/tmp.$SRC $folder/tmp.$TRG
fi

# src
python my_tools/build_dictionary.py $folder/tmp.$SRC
# tgt
if [ $joint_bpe == 0 ];then
  python my_tools/build_dictionary.py  $folder/tmp.$TRG
elif [ $joint_bpe == 1 ]; then
  cp $folder/tmp.$SRC.json $folder/tmp.$TRG.json
fi
rm $folder/tmp.$SRC && rm $folder/tmp.$TRG

# build paddle vocab
python my_tools/json2vocab.py $folder/tmp.$SRC.json $folder/vocab.$SRC
python my_tools/json2vocab.py $folder/tmp.$TRG.json $folder/vocab.$TRG

# build fairseq dict
python my_tools/json2dict.py $folder/tmp.$SRC.json $folder/dict.$SRC.txt
python my_tools/json2dict.py $folder/tmp.$TRG.json $folder/dict.$TRG.txt



# remove
echo "--------------------- remove file ---------------------"
# for prefix in train valid  test.${SRC}_${TRG} test.${TRG}_${SRC} valid.un test.un
#   do
#       for mid in tok dedup clean tc id
#           do
#               if [ -e $folder/$prefix.$mid.$SRC ];then
#                  echo "RM $folder/$prefix.$mid.$SRC"
#                  rm $folder/$prefix.$mid.$SRC
#               fi
#               if [ -e  $folder/$prefix.$mid.$TRG ];then
#                  echo "RM $folder/$prefix.$mid.$TRG"
#                  rm $folder/$prefix.$mid.$TRG
#               fi
#           done

#   done

# mv
out_folder=$folder/${SRC}_${TRG}_bpe
if [ ! -d $out_folder ];then
  echo " mkdir $out_folder"
  mkdir $out_folder
fi

for prefix in train valid  test.${SRC}_${TRG} test.${TRG}_${SRC} valid.un test.un
  do
      if [ -e $folder/$prefix.bpe.$SRC ];then
         mv  $folder/$prefix.bpe.$SRC $out_folder/$prefix.$SRC
      fi
      if [ -e $folder/$prefix.bpe.$TRG ];then
         mv $folder/$prefix.bpe.$TRG $out_folder/$prefix.$TRG
      fi
  done


mv $folder/vocab.* $out_folder/
mv $folder/dict.* $out_folder/
mv model/* $out_folder/

echo "Done!"
