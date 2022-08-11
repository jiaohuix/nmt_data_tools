#!/bin/bash

if [ $# -lt 3 ];then
  echo "usage: bash $0 <workers> <infile> <outfile>"
  exit
fi

workers=$1
infile=$2
outfile=$3

lines=`cat $infile | wc -l`
echo "total lines: $lines"

shard_lines=$((lines/4)) # 每块多少行
tail_lines=$((lines%4)) # 多了多少行
# 分块
for i in $(seq 0 $(($workers-1)))
do
  tail -n +$(($i*$shard_lines+1)) $infile | head -n $shard_lines > $infile.${i}
done
tail -n +$(($workers*$shard_lines+1))  $infile>> $infile.$(($workers-1))


# 执行分词,()和&把for里面需要执行的命令当作一个组合并在后台运行,wait等待所有后台子程序执行完毕再往后运行
for i in $(seq 0 $(($workers-1)))
do
  (
  echo "cut shard:${i}"
  python my_tools/cut_th.py $infile.${i} $infile.cut.${i}
  )&
done
wait

# 结果文件若存在先删除
if [ -e $outfile ];then
  rm $outfile
fi

# 合并并删除分块
for i in $(seq 0 $(($workers-1)))
do
  cat $infile.cut.${i} >> $outfile
  rm $infile.${i} &&  rm $infile.cut.${i}
done
