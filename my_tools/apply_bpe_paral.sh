#!/bin/bash

if [ $# -lt 4 ];then
  echo "usage: bash $0 <infile> <outfile> <workers> <bpe_code>"
  exit
fi

infile=$1
outfile=$2
workers=$3
bpe_code=$4

#export TOOLS=$PWD/nmt_data_tools/
mtools=$TOOLS/my_tools/
source $mtools/func/bpe_func.sh


# Prevent duplicate writes to output files
if [ -e $outfile ];then
  rm $outfile
fi

apply_bpe_parallel $infile $outfile $workers $bpe_code
echo "all done!"
