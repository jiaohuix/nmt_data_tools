#!/bin/sh
# params
if [ $# -lt 5 ];then
 echo "usage: bash $0 <src> <tgt> <in_folder> <out_folder> <topk>"
 exit
fi

src=$1
tgt=$2
in_folder=$3
out_folder=$4
topk=$5
fast_align=fast_align/build
TRAIN=train
VALID=valid
#export TOOLS=$PWD/nmt_data_tools/
mtools=$TOOLS/my_tools/

if [ -d $out_folder ];then
  rm -rf $out_folder
fi
mkdir -p $out_folder

if [ ! -d $fast_align ];then
  echo "build fast align..."
  git clone https://github.com/clab/fast_align.git
  cd fast_align
  mkdir build && cd build
  cmake .. && make
  cd ../..
fi

# merge src tgt
echo "merge src and tgt..."
for prefix in $TRAIN $VALID
  do
    python $mtools/merge_align.py $in_folder/$prefix.$src  $in_folder/$prefix.$tgt $out_folder/$prefix
    cat $out_folder/$prefix >> $out_folder/merge.$src-$tgt
    rm $out_folder/$prefix
  done

# fast align
echo "fast align forward..."
$fast_align/fast_align -i $out_folder/merge.$src-$tgt -d -o -v > $out_folder/forward.align
echo "fast align reverse..."
$fast_align/fast_align -i $out_folder/merge.$src-$tgt -d -o -v -r > $out_folder/reverse.align
echo "fast align symmetrization..."
$fast_align/atools -i $out_folder/forward.align -j $out_folder/reverse.align -c grow-diag-final-and >  $out_folder/$src-$tgt.align

# extract dict
echo "extract dict..."
python $mtools/extract_dict.py $out_folder/merge.$src-$tgt $out_folder/$src-$tgt.align $out_folder/dict.$src-$tgt $topk

echo "all done!"