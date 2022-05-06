#!/bin/bash
echo "function: detokenize and detruecase."
if [ $# -lt 1 ];then
  echo "usage: bash $0 <prefix>"
  exit
fi
prefix=$1
SRC=zh
TRG=en
mosesdecoder=./mosesdecoder

# detokenize
cat $prefix.$TRG | \
 $mosesdecoder/scripts/tokenizer/detokenizer.perl -l $TRG > $prefix.detok.$TRG

# detruecase
$mosesdecoder/scripts/recaser/detruecase.perl  < $prefix.detok.$TRG > $prefix.detrue.$TRG