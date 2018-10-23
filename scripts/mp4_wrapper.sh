#!/bin/sh

# mp4_wrapper.sh
#
# John Newman
#
# Copies all files from input directory into the output directory and
# the .h264 files into .mp4 files.

fps=15

cp -r "$1" "$2"
find "$2" -name "*.h264" | while read file; do
    MP4Box -fps "$fps" -add "$file" ${file%.*}.mp4
    rm "$file"
done
open "$2"
