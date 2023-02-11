#!/bin/bash
#export TOOLS=$PWD/nmt_data_tools/
mtools=$TOOLS/my_tools/
source $mtools/func/shard_func.sh

function apply_spm() {
    local infile=$1
    local outfile=$2
    local spm_model=$3

    python $mtools/spm_encode.py \
           --model $spm_model \
           --output_format=piece \
           --inputs=$infile \
           --outputs=$outfile
}

function apply_spm_parallel(){
    local workers=$1
    local src=$2
    local tgt=$3
    local inprefix=$4 # out: inpefix.spm.lang
    local spm_model=$5

    # func_paral_process  <cmd> <script> <infile> <outfile> <workers> <options>
    commands_src="func apply_spm $inprefix.${src} $inprefix.spm.${src} $workers $spm_model"
    commands_tgt="func apply_spm $inprefix.${tgt} $inprefix.spm.${tgt} $workers $spm_model"
    echo "---------------------- Apply spm to src.----------------------"
    func_paral_process  $commands_src
    echo "---------------------- Apply spm to tgt.----------------------"
    func_paral_process  $commands_tgt
}

