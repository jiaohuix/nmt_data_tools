#!/bin/bash

if [ $# -lt 5 ];then
  echo "usage: bash $0 <workers> <src> <tgt> <inprefix> <spm_model>"
  exit
fi

workers=$1
src=$2
tgt=$3
inprefix=$4
spm_model=$5

#export TOOLS=$PWD/nmt_data_tools/
mtools=$TOOLS/my_tools/
source $mtools/func/spm_func.sh


apply_spm_parallel $workers $src $tgt $inprefix $spm_model
echo "all done!"
