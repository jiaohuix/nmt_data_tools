if [ $# -lt 5 ];then
  echo "usage: bash $0 <src> <tgt> <prefix> <scorefile> <order=0/1>"
  exit
fi

src=$1
tgt=$2
prefix=$3
scorefile=$4
order=$5

python rank.py $prefix.${src} $prefix.sorted.${src} $scorefile  ${order}
python rank.py $prefix.${tgt} $prefix.sorted.${tgt} $scorefile  ${order}