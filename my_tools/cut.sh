#!/bin/bash

if [ $# -lt 3 ];then
  echo "usage: bash $0 <workers> <infile> <outfile> <lang>(opt) <backend>(opt) <userdict>(opt)"
  echo "<lang>: only support  lang=(zh, th), default=zh."
  echo "<backend>: chinese segment backend, choices=(jieba, thulac), default=jieba."
  echo "<userdict>: chinese user dict."
  exit
fi

# cmd var
workers=$1
infile=$2
outfile=$3
lang=${4:-"zh"}
backend=${5:-"jieba"}
userdict=${6:-""}
cmd="python"
# env var
#export TOOLS=$PWD/nmt_data_tools/
mtools=$TOOLS/my_tools/
source $mtools/func/shard_func.sh

py_script=$mtools/cut.py
optional="$backend   $userdict"
if [ "$lang"x == "th"x ]
  then
    py_script=$mtools/cut_th.py
    optional=""
fi


echo "cmd:  $cmd $py_script $infile $outfile $optional"
func_paral_process $cmd $py_script $infile $outfile $workers $optional

echo "all done!"

