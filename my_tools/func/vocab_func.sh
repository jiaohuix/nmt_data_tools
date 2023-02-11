#!/bin/bash
#export TOOLS=$PWD/nmt_data_tools/
mtools=$TOOLS/my_tools/
source $mtools/func/shard_func.sh

function paral_word_count(){
    local workers=$1
    local infile=$2
    # 1.shard [infile->infile.worker_id]
    func_shard $workers $infile

    # 2.parallel process [infile.worker_id -> infile.worker_id.json]
    for i in $(seq 0 $(($workers-1)))
    do
      (
      echo "---------------------- Counting shard${i}'s words .----------------------"
      #
      python $mtools/build_dictionary.py $infile.${i}
      rm $infile.${i}
      )&
    done
    wait

    # 3.merge json [infile.worker_id.json -> infile.json]
    ## json files path array
    json_files=()
    for i in $(seq 0 $(($workers-1)))
      do
          json_files+=("${infile}.${i}.json")
      done
    ## merge json fikes
    echo "merging json files: ${json_files[@]}"
    python $mtools/merge_json.py  "${json_files[@]}"

    ## rm tmp json files
    for file in ${json_files[@]}
      do
          rm $file
      done
}


function build_vocab_parallel() {
    # build_vocab_parallel <src> <tgt> <outfolder> <workers> <joint> <freq> <data_prefixes...>
    local src=$1
    local tgt=$2
    local outfolder=$3  #
    local workers=$4  #
    local joint=${5:-"n"} #y/n
    local freq=${6:-"n"} #y/n
    shift 6
    local data_prefixes=$@

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
        echo "----- make joint vocab. ----- "
        cat ${outfolder}/tmp.${tgt} >> ${outfolder}/tmp.${src}
    fi

    # 3 make vocab
    paral_word_count $workers ${outfolder}/tmp.${src}

    if [ "$joint"x == "n"x ]
    then
        paral_word_count $workers   ${outfolder}/tmp.${tgt}
    elif [ "$joint"x == "y"x ]
    then
        cp  ${outfolder}/tmp.${src}.json  ${outfolder}/tmp.${tgt}.json
    fi

    # build paddle vocab
    python $mtools/json2vocab.py ${outfolder}/tmp.${src}.json  ${outfolder}/vocab.${src}  $freq
    python $mtools/json2vocab.py ${outfolder}/tmp.${tgt}.json  ${outfolder}/vocab.${tgt}  $freq

    # build fairseq dict
    python $mtools/json2dict.py ${outfolder}/tmp.${src}.json  ${outfolder}/dict.${src}.txt  $freq
    python $mtools/json2dict.py ${outfolder}/tmp.${tgt}.json  ${outfolder}/dict.${tgt}.txt  $freq

    rm ${outfolder}/tmp.*
    echo "src and tgt bpe file already learned."

}

