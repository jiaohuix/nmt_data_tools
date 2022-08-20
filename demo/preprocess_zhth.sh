#!/bin/sh



#folder=data
folder=$1
SRC=zh
TRG=th

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
# lang id ratio
#threshold=0.3

#if [ ! -d mosesdecoder ];then
#  git clone https://github.com/moses-smt/mosesdecoder.git
#fi
#mosesdecoder=./mosesdecoder
#SCRIPTS=mosesdecoder/scripts
#TOKENIZER=$SCRIPTS/tokenizer/tokenizer.perl
#LC=$SCRIPTS/tokenizer/lowercase.perl
#CLEAN=$SCRIPTS/training/clean-corpus-n.perl
#BPEROOT=subword-nmt/subword_nmt


echo "-------------- clean  opensubtitles zh-thai--------------"
python $folder/zh_thai_opensubtitles_filter.py  $folder/train.sub   $folder/train.clean_sub th zh

# train valid split
echo  "-------------- train dev split --------------"
# train valid split(ikcest),merge ikcest and opensubtitles
python my_tools/train_dev_split.py $SRC $TRG $folder/train.ikcest $folder/ $valid_num # train.lang/ dev.lang
mv $folder/dev.$SRC  $folder/valid.$SRC && mv $folder/dev.$TRG  $folder/valid.$TRG
cat $folder/train.clean_sub.$SRC  >> $folder/train.$SRC
cat $folder/train.clean_sub.$TRG  >> $folder/train.$TRG

raw_lines=$(cat $folder/train.$SRC | wc -l )
echo "raw lines: $raw_lines"


# tokenize
echo "--------------tokenize --------------"
for prefix in train valid mono  test.${SRC}_${TRG} test.${TRG}_${SRC}
  do
    if [ -e $folder/$prefix.$SRC ];then
       echo "tokenize $prefix.$SRC"
#       bash my_tools/cut.sh 4 $folder/$prefix.$SRC  $folder/$prefix.tok.$SRC # jieba分词
        python my_tools/cut_multi.py $folder/$prefix.$SRC  $folder/$prefix.tok.$SRC 4 $SRC
    fi

    if [ -e $folder/$prefix.$TRG ];then
       echo "tokenize $prefix.$TRG"
       python my_tools/cut_multi.py $folder/$prefix.$TRG  $folder/$prefix.tok.$TRG 4 $TRG
#       bash my_tools/cut_th.sh 4 $folder/$prefix.$TRG  $folder/$prefix.tok.$TRG # pyhainlp
    fi
  done



echo  "-------------- chinese error/low_freq words filter --------------"
python my_tools//zh_abnormal_filter.py --zh-lang $SRC --other-lang $TRG --in-prefix $folder/train.tok --out-prefix  $folder/train.clean --threshold 0.45 --min-freq 20 --wt
mv $folder/train.clean.$SRC $folder/train.tok.$SRC && mv $folder/train.clean.$TRG $folder/train.tok.$TRG

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


# clean empty and long sentences, and sentences with high source-target ratio (training corpus only)
#$mosesdecoder/scripts/training/clean-corpus-n.perl -ratio $lengRatio $folder/train.dedup $SRC $TRG $folder/train.clean $lower $upper

# do length filter after bpe, check statistic info first
python my_tools/check_pair.py $folder/train.tok $SRC $TRG  $upper $lengRatio 0


# lang id filter，只过滤train (不要过滤了，全是错的)
#if [ ! -e lid.176.bin ];then
# wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
#fi

#python ./my_tools/data_filter.py --src-lang $SRC --tgt-lang $TRG --in-prefix $folder/train.clean --out-prefix $folder/train.tok
#lang_filt_lines=$(cat $folder/train.tok.$SRC | wc -l )
#echo "--------------[lang_filt result]: [$lang_filt_lines/$length_filt_lines]. --------------"
#python my_tools/compare_2file.py $folder/train.clean.$SRC  $folder/train.tok.$SRC folder/train.cmp_id.$SRC
#mv  $folder/train.tok.$SRC  $folder/train.rtok.$SRC && mv  $folder/train.tok.$TRG  $folder/train.rtok.$TRG
#mv $folder/train.clean.$SRC   $folder/train.tok.$SRC  && mv   $folder/train.clean.$TRG   $folder/train.tok.$TRG


echo "-------------- learn bpe --------------"
if [ ! -d model ];then
  mkdir model
fi
## train BPE, do not joint source and target bpe

cat $folder/train.tok.$SRC > $folder/tmp.$SRC
if [ -e $folder/mono.tok.$SRC ];then
  cat $folder/mono.tok.$SRC >> $folder/tmp.$SRC
fi

cat $folder/train.tok.$TRG > $folder/tmp.$TRG

if [ -e $folder/mono.tok.$TRG ];then
  cat $folder/mono.tok.$TRG >> $folder/tmp.$TRG
fi

if [ $joint_bpe == 1 ];then
  echo "------- learn joint bpe ------- "
  cat $folder/tmp.$TRG >> $folder/tmp.$SRC
#  cp $folder/tmp.$SRC $folder/tmp.$TRG
fi

wc $folder/tmp.$SRC
wc $folder/tmp.$TRG

subword-nmt learn-bpe -s $src_bpe_operations < $folder/tmp.$SRC  > model/$SRC.bpe

if [ $joint_bpe == 0 ];then
  subword-nmt learn-bpe -s $src_bpe_operations < $folder/tmp.$TRG > model/$TRG.bpe
elif [ $joint_bpe == 1 ]; then
  cp model/$SRC.bpe model/$TRG.bpe
fi


# joint bpe
# cat $folder/train.tc.$SRC $folder/train.tc.$TRG  | $subword_nmt/learn_bpe.py -s $src_bpe_operations > model/$SRC.bpe

# apply BPE
echo "--------------apply BPE--------------"
for prefix in train valid mono  test.${SRC}_${TRG} test.${TRG}_${SRC}
 do
   if [ -e $folder/$prefix.$SRC ];then
      echo "bpe $prefix.$SRC"
      subword-nmt apply-bpe -c model/$SRC.bpe < $folder/$prefix.tok.$SRC  >  $folder/$prefix.bpe.$SRC
   fi
   if [ -e $folder/$prefix.$TRG ];then
      echo "bpe $prefix.$TRG"
      subword-nmt apply-bpe -c  model/$TRG.bpe < $folder/$prefix.tok.$TRG > $folder/$prefix.bpe.$TRG
   fi
 done


#build network dictionary
echo "--------------build network dictionary--------------"
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
#  cp $folder/tmp.$SRC $folder/tmp.$TRG
fi

#cat $folder/train.bpe.$SRC   > $folder/tmp.$SRC
#cat $folder/train.bpe.$TRG $folder/mono.bpe.$TRG  > $folder/tmp.$TRG
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


# firstly do bpe and get vocab, and then do length filt
#perl $CLEAN -ratio $lengRatio $folder/train.bpe $SRC $TRG $folder/train.clean $lower $upper
#length_filt_lines=$(cat $folder/train.clean.$SRC | wc -l )
#echo "--------------[Length filter result]: [$length_filt_lines/$raw_lines]. --------------"


# remove
echo "--------------remove file--------------"
#for prefix in train valid mono  test.${SRC}_${TRG} test.${TRG}_${SRC}
#  do
#      for mid in tok clean tc id dedup
#          do
#              if [ -e $folder/$prefix.$mid.$SRC ];then
#                 echo "RM $folder/$prefix.$mid.$SRC"
#                 rm $folder/$prefix.$mid.$SRC
#              fi
#              if [ -e  $folder/$prefix.$mid.$TRG ];then
#                 echo "RM $folder/$prefix.$mid.$TRG"
#                 rm $folder/$prefix.$mid.$TRG
#              fi
#          done
#
#  done

# mv
out_folder=$folder/${SRC}_${TRG}_bpe
if [ ! -d $out_folder ];then
  echo " mkdir $out_folder"
  mkdir $out_folder
fi

for prefix in train valid mono  test.${SRC}_${TRG} test.${TRG}_${SRC}
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
