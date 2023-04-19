#!/bin/bash
if [ $# -lt 3 ];then
  echo "usage: bash $0 <file1> <file2> <outfile>  <sep=[SEP]>(opt)"
  echo "merge k times"
  exit
fi
file1=$1
file2=$2
outfile=$3
sep=${4:-"[SEP]"}

awk 'BEGIN{FS="\n";OFS=" [SEP] "} {getline f2 < "'"$file2"'"; print $0,f2}' $file1 > $outfile
echo "write to file $outfile success."

