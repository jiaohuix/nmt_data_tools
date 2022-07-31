#!/bin/sh
# params
#if [ $# -lt 3 ];then
#  echo "usage: bash $0 <workers> <infile> <outfile>"
#  exit
#fi
#workers=$1

src=zh
tgt=en
topk=1000
in_folder=data
out_folder=data/fast_align
fast_align=fast_align/build
TRAIN=train
VALID=dev

rm -rf $out_folder
mkdir $out_folder

if [ ! -d $fast_align ];then
  git clone https://github.com/clab/fast_align.git
  cd fast_align
  mkdir build && cd build
  cmake .. && make
  cd ..
fi

# merge src tgt
for prefix in $TRAIN $VALID
  do
    python my_tools/merge_align.py $in_folder/$prefix.$src  $in_folder/$prefix.$tgt $out_folder/$prefix
    cat $out_folder/$prefix >> $out_folder/merge.$src-$tgt
    rm $out_folder/$prefix
  done

# fast align
$fast_align/fast_align -i $out_folder/merge.$src-$tgt -d -o -v > $out_folder/forward.align
$fast_align/fast_align -i $out_folder/merge.$src-$tgt -d -o -v -r > $out_folder/reverse.align
$fast_align/atools -i $out_folder/forward.align -j $out_folder/reverse.align -c grow-diag-final-and >  $out_folder/$src-$tgt.align

# extract dict
python my_tools/extract_dict.py $out_folder/merge.$src-$tgt $out_folder/$src-$tgt.align $out_folder/dict.$src-$tgt $topk