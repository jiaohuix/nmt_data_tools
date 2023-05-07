#!/bin/bash
if [ $# -lt 3 ];then
  echo "usage: bash $0 <src> <tgt> <folder> <prefix=train>(opt)"
  exit
fi
src=$1
tgt=$2
folder=$3
prefix=${4:-"train"}

paste $folder/$prefix.$src $folder/$prefix.$tgt  | sed 's/ *\t */ ||| /g' > $folder/$prefix.${src}-${tgt}
echo "train forward model..."
./fast_align/build/fast_align -i $folder/$prefix.${src}-${tgt} -d -v -o -p $folder/$prefix.fwd_params > $folder/$prefix.fwd_align
echo "train backward model..."
./fast_align/build/fast_align -i $folder/$prefix.${src}-${tgt}  -r -d -v -o -p $folder/$prefix.rev_params > $folder/$prefix.rev_align
echo "generates asymmetric alignments..."
./fast_align/build/atools  -i $folder/$prefix.fwd_align -j $folder/$prefix.rev_align -c grow-diag-final-and > $folder/$prefix.sym_align

echo "done"