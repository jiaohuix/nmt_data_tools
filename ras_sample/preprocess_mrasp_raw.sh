#!/bin/sh

in_folder=$1
out_folder=$2
src=$3
tgt=$4

valid_lines=`cat $in_folder/valid.$src | wc -l`

rm -rf $out_folder
mkdir -p $out_folder

# vocab
head -n 4 $in_folder/vocab.$src > $out_folder/vocab.src && echo "<$src>" >> $out_folder/vocab.src && echo "<$tgt>" >> $out_folder/vocab.src
tail -n +5 $in_folder/vocab.$src >> $out_folder/vocab.src
cat $out_folder/vocab.src > $out_folder/vocab.tgt

# add tag
for prefix in train valid test
  do
    sed "s/^/<$src> /g" $in_folder/$prefix.$src > $out_folder/$prefix.tag.$src
    sed "s/^/<$tgt> /g" $in_folder/$prefix.$tgt > $out_folder/$prefix.tag.$tgt
  done
# source mono tag
if [ -e $in_folder/mono.$src ];then
    sed "s/^/<$src> /g"  $in_folder/mono.$src > $out_folder/mono.tag.$src
fi
# target mono tag
if [ -e $in_folder/mono.$tgt ];then
      sed "s/^/<$tgt> /g"  $in_folder/mono.$tgt > $out_folder/mono.tag.$tgt
fi


# merge train和valid的src tgt， test不动 [new:添加单语]
for prefix in train valid
  do
    # bidirection
    cat $out_folder/$prefix.tag.$src  $out_folder/$prefix.tag.$tgt > $out_folder/$prefix.tag.src
    cat $out_folder/$prefix.tag.$tgt  $out_folder/$prefix.tag.$src > $out_folder/$prefix.tag.tgt
  done

# merge source mono
if [ -e $in_folder/mono.$src ];then
    cat $out_folder/mono.tag.$src >> $out_folder/train.tag.src && cat $out_folder/mono.tag.$src >> $out_folder/train.tag.tgt
    rm $out_folder/mono.tag.$src
fi
# merge target mono
if [ -e $in_folder/mono.$tgt ];then
    cat $out_folder/mono.tag.$tgt  >> $out_folder/train.tag.src && cat $out_folder/mono.tag.$tgt >> $out_folder/train.tag.tgt
    rm $out_folder/mono.tag.$tgt
fi

# rename test file
mv $out_folder/test.tag.$src $out_folder/test.src && mv $out_folder/test.tag.$tgt $out_folder/test.tgt


# shuffle train valid   prefix.lang ->shuffle.lang
for prefix in train valid
  do
    python my_tools/shuffle_pair.py src tgt $out_folder/$prefix.tag $out_folder/
    mv $out_folder/shuffle.src  $out_folder/$prefix.src && mv $out_folder/shuffle.tgt  $out_folder/$prefix.tgt
    rm $out_folder/$prefix.tag.src  && rm $out_folder/$prefix.tag.tgt
  done

# subsample valid  (final sub)
#mv $out_folder/valid.src $out_folder/valid.tmp.src && head -n $valid_lines $out_folder/valid.tmp.src> $out_folder/valid.src
#mv $out_folder/valid.tgt $out_folder/valid.tmp.tgt && head -n $valid_lines $out_folder/valid.tmp.tgt> $out_folder/valid.tgt
#rm $out_folder/valid.tmp.src && rm $out_folder/valid.tmp.tgt


for prefix in train valid
  do
    rm $out_folder/$prefix.tag.$src
    rm $out_folder/$prefix.tag.$tgt
  done

ls $out_folder
