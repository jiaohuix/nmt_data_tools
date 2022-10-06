#!/bin/sh
folder=$1
prefix=$2
bpe_code=$3
src=$4
tgt=$5

# merge tgt first
echo "--------------------Merge tgt ras file.--------------------"
cat $folder/${prefix}.tgt  $folder/expanded_${prefix}.tgt >  $folder/${prefix}.ras.tgt
cp $bpe_code  $folder/code

# src: tok->bpe->id
# moses -> expanded_${prefix}.tok.src
echo "--------------------Tokenize src file.--------------------"
#bash moses_mix_lang.sh <in_prefix> <in_suffix> <src_lang> <tgt_lang> <outfile>
moses_arr=("en","es","fr","de","ru")
if echo ${moses_arr[@]} | grep -w $src &>/dev/null
  then
      echo "do moses."
      bash ras_sample/moses_mix_lang.sh $folder/expanded_${prefix} src $src $tgt $folder/expanded_${prefix}.tok.src
  else
     echo "do copy."
     cp $folder/expanded_${prefix}.src $folder/expanded_${prefix}.tok.src
fi



## bpe (看看bpe会不会影响<lang>)
echo "--------------------Bpe src file.--------------------"
subword-nmt apply-bpe -c $bpe_code < $folder/expanded_${prefix}.tok.src > $folder/expanded_${prefix}.bpe.src

# paste id
echo "--------------------Paste lang token.--------------------"
#paste -d " " $folder/lang_indicator.src  $folder/expanded_${prefix}.bpe.src > $folder/expanded_${prefix}.id.src
python my_tools/merge.py $folder/lang_indicator.src $folder/expanded_${prefix}.bpe.src  $folder/expanded_${prefix}.id.src space


# merge
echo "--------------------Merge src ras file.--------------------"
cat $folder/${prefix}.src  $folder/expanded_${prefix}.id.src >  $folder/${prefix}.ras.src
rm $folder/expanded_${prefix}.tok.src && rm $folder/expanded_${prefix}.bpe.src && rm $folder/expanded_${prefix}.id.src
rm  $folder/expanded_${prefix}.tgt && rm $folder/expanded_${prefix}.src && rm $folder/lang_indicator.src


# shuffle train valid   prefix.ras.lang -> shuffle.lang
echo "--------------------Shuffle ras file.--------------------"
python my_tools/shuffle_pair.py src tgt $folder/$prefix.ras   $folder/
mv $folder/shuffle.src $folder/$prefix.ras.src && mv $folder/shuffle.tgt $folder/$prefix.ras.tgt

# subsample valid
# echo "--------------------Subsample valid ras file.--------------------"
# if [ "$prefix"x = "valid"x ];then
#   head -n 5000 $folder/$prefix.ras.src > $folder/tmp.src
#   head -n 5000 $folder/$prefix.ras.tgt > $folder/tmp.tgt
#   mv $folder/tmp.src  $folder/$prefix.ras.src
#   mv $folder/tmp.tgt  $folder/$prefix.ras.tgt
# fi

echo "Done!"
