#!/bin/bash

if [ $# -lt 2 ];then
  echo "usage: bash $0 <workers> <infile> "
  exit
fi

workers=$1
infile=$2

#export TOOLS=$PWD/nmt_data_tools/
mtools=$TOOLS/my_tools/
source $mtools/func/vocab_func.sh

paral_word_count $workers $infile
echo "all done!"
