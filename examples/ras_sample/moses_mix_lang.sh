#!/bin/sh

prefix=$1
surfix=$2
src=$3
tgt=$4
outfile=$5

SCRIPTS=mosesdecoder/scripts
TOKENIZER=$SCRIPTS/tokenizer/tokenizer.perl

# split file by language token ->prefix.de, prefix.en, prefix.idx
echo "--------------------Split file.--------------------"
python my_tools/split_merge_lang.py --prefix $prefix --langs $surfix --mode split

# moses tokenize
echo "--------------------Moses tokenize.--------------------"
cat $prefix.$src | perl $TOKENIZER -threads 8 -l $src > $prefix.tok.$src
cat $prefix.$tgt | perl $TOKENIZER -threads 8 -l $tgt > $prefix.tok.$tgt
mv $prefix.idx $prefix.tok.idx
rm $prefix.$src && rm $prefix.$tgt


## merge all file ->prefix.merge
echo "--------------------Merge file.--------------------"
python my_tools/split_merge_lang.py --prefix $prefix.tok --langs ${src},${tgt} --mode merge --remove-lang

## rename file
mv $prefix.tok.merge $outfile
echo "Done moses."
