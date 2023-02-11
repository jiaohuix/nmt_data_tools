if [ $# -lt 3 ];then
  echo "usage: bash $0 <prefix> <lang> <num_shards>(default=4) "
  exit
fi
prefix=$1
lang=$2
workers=${3:-4}
infile=${prefix}.${lang}

#export TOOLS=$PWD/nmt_data_tools/
mtools=$TOOLS/my_tools/
source $mtools/func/shard_func.sh
func_shard $workers $infile

for i in $(seq 0 $(($workers-1)))
do
  mv $infile.${i} ${prefix}.${i}.${lang}
done
