#!/bin/bash

if [ $# -lt 4 ];then
  echo "usage: bash $0 <workers> <infile> <outfile> <bpe_code>"
  exit
fi

workers=$1
infile=$2
outfile=$3
bpe_code=$4


source my_tools/shard_func.sh

function paral_bpe(){
    local workers=$1
    local infile=$2
    local outfile=$3
    local bpe_code=$4

    # 1.shard [infile->infile.worker_id]
    echo "---------------------- Sharding files.----------------------"
    func_shard $workers $infile

    # 2.parallel process [infile.worker_id -> infile.worker_id.bpe]
    for i in $(seq 0 $(($workers-1)))
    do
      (
      echo "---------------------- Apply bpe to shard${i}'s.----------------------"
      #
      subword-nmt apply-bpe -c $bpe_code <  $infile.${i} >  $infile.${i}.bpe
      rm $infile.${i}
      )&
    done
    wait

    # 3.merge files [infile.worker_id.bpe -> infile.bpe]
    for i in $(seq 0 $(($workers-1)))
      do
          cat $infile.${i}.bpe >> $outfile
          rm $infile.${i}.bpe
      done

}

rm $outfile
paral_bpe $workers $infile $outfile $bpe_code
echo "all done!"
