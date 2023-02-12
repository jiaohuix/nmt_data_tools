#!/bin/bash

if [ $# -lt 3 ];then
  echo "usage: bash $0 <infile> <outfile> <bpe_code> <workers=4>(opt) <num_iter=5>(opt) <drop_rate=0.1>(opt)  "
  exit
fi

infile=$1
outfile=$2
bpe_code=$3
workers=${4:-4}
num_iter=${5:-5}
drop_rate=${6:-0.1}

#export TOOLS=$PWD/nmt_data_tools/
mtools=$TOOLS/my_tools/
source $mtools/func/shard_func.sh


# Prevent duplicate writes to output files
if [ -e $outfile ];then
  rm $outfile
fi


command="python $mtools/bpe_dropout.py $infile $outfile $workers $bpe_code $num_iter $drop_rate"
func_paral_process $command
echo "all done!"
