#!/bin/bash

# reverse given files or files in 
# the given directory.

BASEDIR=`dirname $0`;
FFMPEG="$HOME/Desktop/tmp/vc/bin/ffmpeg"
SRCDIR=`realpath $1`

function usage() {
	echo "Usage: $0 [directory|file.mp4 file2.mp4 ...]"
}

if [ "$1" = "" ]; then
	usage;
	exit 1;
fi
if [ -d "$1" ]; then
    FILES=`ls $1/*.mp4`
else
    FILES="$@"
fi

for FILE in $FILES; do
    echo Reversing $FILE ...
    BASENAME=`basename $FILE .mp4`
    SRCDIR=`dirname $FILE`
    OUTFILE="r$BASENAME.mp4"

    if [ ! -f "$SRCDIR/$OUTFILE" ]; then
       
        $FFMPEG -i "$FILE" -vf reverse "$SRCDIR/$OUTFILE"

        echo Created "$SRCDIR/$OUTFILE" .
        echo
    else
        echo Exists: "$SRCDIR/$OUTFILE" .
        echo
    fi
    
done