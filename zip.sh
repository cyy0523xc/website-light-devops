#!/bin/bash
# 
# 将项目打包压缩（用于正式打包）
# Author: alex
# Created Time: 2020年05月10日 星期日
cd ../
name="website-light-devops"
if [ ! -d "$name" ]; then
    echo "$PWD: 当前目录错误."
fi
version=
if [ $# = 1 ]; then 
    version="-$1"
fi

# 删除旧的打包文件
date_str=`date -I`
filename="$name-${date_str//-/}$version".tar.gz
if [ -f "$filename" ]; then
    rm -f "$filename"
fi

# 打包src目录和readme文件
tar -zcvf "$filename" \
    --exclude ".git" \
    --exclude ".*" \
    --exclude ".swp" \
    --exclude "__pycache__" \
    --exclude "settings.py" \
    "$name/src" "$name/README.md"

date
echo "$filename"
echo ""
echo ""
