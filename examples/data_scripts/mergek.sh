#!/bin/bash
if [ $# -lt 2 ];then
  echo "usage: bash $0 <infolder> <outfolder> <k=2>(opt) <prefix=train>(opt)"
  echo "merge k times"
  exit
fi

src=src
tgt=tgt
infolder=$1
outfolder=$2
k=${3:-"1"}
prefix=${4:-"train"}


if [ ! -d $outfolder ];then
  mkdir -p $outfolder
fi

for i in $(seq 1 $k)
do
  # train.src/tgt
#  seed=1
  seed=$i
  echo "shuffle..."
  shuf --random-source=<(yes $seed) $infolder/$prefix.$src >  $outfolder/$prefix.shuf.$src
  shuf --random-source=<(yes $seed) $infolder/$prefix.$tgt >  $outfolder/$prefix.shuf.$tgt
  echo "merge res2"
  # merge res2
  srcfile2=$outfolder/$prefix.shuf.$src
  tgtfile2=$outfolder/$prefix.shuf.$tgt
  awk 'BEGIN{FS="\n";OFS=" [SEP] "} {getline f2 < "'"$srcfile2"'"; print $0,f2}' $infolder/$prefix.$src >  $outfolder/$prefix.res2.$src
  awk 'BEGIN{FS="\n";OFS=" [SEP] "} {getline f2 < "'"$tgtfile2"'"; print $0,f2}' $infolder/$prefix.$tgt >  $outfolder/$prefix.res2.$tgt

  cat $infolder/$prefix.$src  $infolder/$prefix.$src $outfolder/$prefix.res2.$src >> $outfolder/$prefix.$src
  cat $infolder/$prefix.$tgt  $infolder/$prefix.$tgt $outfolder/$prefix.res2.$tgt >> $outfolder/$prefix.$tgt

done


paste $outfolder/$prefix.$src $outfolder/$prefix.$tgt > $outfolder/$prefix
cp  $infolder/valid $outfolder
cp  $infolder/test  $outfolder



