#!/bin/bash
#export TOOLS=$PWD/nmt_data_tools/
mtools=$TOOLS/my_tools/
source $mtools/func/shard_func.sh

function learn_bpe(){
    # learn_bpe <src> <tgt> <outfolder> <joint> <operations>  <data_prefixes...>
    local src=$1
    local tgt=$2
    local outfolder=$3  #     # codes.bpe.ops
    local joint=${4:-"n"} #y/n
    local ops=${5:-8000}
    shift 5
    local data_prefixes=$@
    # if has bpe codes, exit
    bpefile_src=${outfolder}/${src}.bpe.${ops}
    bpefile_tgt=${outfolder}/${tgt}.bpe.${ops}
#    if [ -e $bpefile_src ] && [ -e $bpefile_tgt ];then
#      echo "src and tgt bpe file already exists."
#      exit
#    fi
    if [ ! -d $outfolder ];then
      mkdir -p $outfolder
    fi
    # 1 merget src and tgt corpus seperately
    for prefix in $data_prefixes
      do
        if [ -e ${data_prefixes}.${src} ];then
          cat ${data_prefixes}.${src} >> ${outfolder}/tmp.${src}
        fi
        if [ -e ${data_prefixes}.${tgt} ];then
          cat ${data_prefixes}.${tgt} >> ${outfolder}/tmp.${tgt}
        fi
      done

    # 2 merge src and tgt corpus if joint=y
    if [ "$joint"x == "y"x ];then
        echo "----- learn joint bpe. ----- "
        # TODO: resample
        cat ${outfolder}/tmp.${tgt} >> ${outfolder}/tmp.${src}
    fi

    # 3 learn bpe
    wc ${outfolder}/tmp.${src}
    wc ${outfolder}/tmp.${tgt}

    subword-nmt learn-bpe -s $ops < ${outfolder}/tmp.${src}  > $bpefile_src
    if [ "$joint"x == "n"x ]
    then
        subword-nmt learn-bpe -s $ops < ${outfolder}/tmp.${tgt} > $bpefile_tgt
    elif [ "$joint"x == "y"x ]
    then
        cp  $bpefile_src  $bpefile_tgt
        cp  $bpefile_src  ${outfolder}/${src}${tgt}.bpe.${ops}

    fi

    rm ${outfolder}/tmp.*
    echo "src and tgt bpe file already learned."

}

function apply_bpe(){
      local infile=$1
      local outfile=$2
      local bpe_code=$3
      subword-nmt apply-bpe -c $bpe_code < $infile >  $outfile
}


function apply_bpe_parallel(){
    local infile=$1
    local outfile=$2
    local workers=$3
    local bpe_code=$4

    # func_paral_process  <cmd> <script> <infile> <outfile> <workers> <options>
    commands="func apply_bpe $infile $outfile $workers $bpe_code"
    func_paral_process  $commands
}


