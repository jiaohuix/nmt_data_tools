#!/usr/bin/env bash
if [ $# -lt 3 ];then
  echo "usage: bash $0 <lang> <infolder> <outfolder>"
  exit
fi
lng=$1
infolder=$2
outfolder=$3

if [ ! -d $outfolder ];then
  mkdir -p $outfolder
fi

echo "src lng $lng"
scripts=nmt_data_tools/mosesdecoder/scripts/
for sub  in train valid test
do
    sed -r 's/(@@ )|(@@ ?$)//g' $infolder/${sub}.${lng} > $infolder/${sub}.${lng}.tok
    perl $scripts/tokenizer/detokenizer.perl -l $lng < $infolder/${sub}.${lng}.tok > $outfolder/${sub}.${lng}
    rm $infolder/${sub}.${lng}.tok
done

