#!/bin/bash

if [ $# -lt 2 ];then
  echo "usage: bash $0 <workers> <infile> "
  exit
fi

workers=$1
infile=$2


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

paral_word_count $workers $infile
echo "all done!"