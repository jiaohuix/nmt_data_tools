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
source $mtools/func/shard_func.sh

function paral_spm(){
    local workers=$1
    local src=$2
    local tgt=$3
    local inprefix=$4
    local spm_model=$5

    # 1.shard [inprefix.lang->inprefix.lang.worker_id]
    echo "---------------------- Sharding files.----------------------"
    func_shard $workers $inprefix.${src}
    func_shard $workers $inprefix.${tgt}

    # 2.parallel process [inprefix.lang.worker_id -> inprefix.spm.lang.worker_id]
    for i in $(seq 0 $(($workers-1)))
    do
      (
      echo "---------------------- Apply spm to shard${i}'s.----------------------"
      for lang in $src $tgt
          do
            python scripts/spm_encode.py \
                   --model $spm_model \
                   --output_format=piece \
                   --inputs=$inprefix.$lang.${i} \
                   --outputs=$inprefix.spm.$lang.${i}

            rm $inprefix.$lang.${i}
          done

      )&
    done
    wait
    echo "-------- merge --------"
    # 3.merge files [inprefix.spm.lang.worker_id -> inprefix.spm.lang]
    touch $inprefix.spm.${src}
    touch $inprefix.spm.${tgt}
    for i in $(seq 0 $(($workers-1)))
      do
          cat  $inprefix.spm.${src}.${i} >> $inprefix.spm.${src}
          cat  $inprefix.spm.${tgt}.${i} >> $inprefix.spm.${tgt}
          rm $inprefix.spm.${src}.${i} && rm $inprefix.spm.${tgt}.${i}
      done

}

paral_spm $workers $src $tgt $inprefix $spm_model
echo "all done!"