#!/bin/sh
# 将目录下所有含有xml文件的文件夹中，所有的xml转成txt，并输出到新的目录，目录结构不变
# root
#   -folder1
#      -- a.xml
#       -- aa.txt
####### 转为 #######
# root
#   -folder1
#       -- a.txt

if [ $# -lt 2 ];then
  echo "usage: bash $0 <infolder> <outfolder>"
  exit
fi
root=$1
out_root=$2

#export TOOLS=$PWD/nmt_data_tools/
mtools=$TOOLS/my_tools/


# 遍历所有含有xml的文件夹
for folder in ` ls $root `
  do
    if [ -d $root/$folder ];then
        # 遍历文件夹下所有xml或sgm文件
        for file in `ls $root/$folder`
        do
          if [ -e $root/$folder/$file ];then
              if  [ "${file##*.}"x = "xml"x ] ||  [ "${file##*.}"x = "sgm"x ] ||  [ "${file##*.}"x = "tmx"x ];then
                # 核心操作
                echo "processing $folder/$file"
                # 递归创建文件夹
                if [ ! -d $out_root/$folder ];then
                  mkdir -p $out_root/$folder
                fi
                # xml转txt文件，并输出到out_root目录下相同位置
                python $mtools/process_xml.py $root/$folder/$file $out_root/$folder
              fi
          fi
        done

    fi
  done

echo "preprocess over."
