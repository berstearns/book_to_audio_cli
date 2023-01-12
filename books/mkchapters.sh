#!/bin/bash

# $1 foldername from ./books folder as root
# $2 the colum number of the name of the chapter
for name in `cat $1/chapters.tsv| grep "^[^#]" | cut -d "	" -f$2 | awk '{ gsub(" ","-",$0); print tolower($0) }'`;
do
    mkdir $1/$name
done
