#!/bin/bash

BASEDIR=`dirname $0`;
FFMPEG="$HOME/Desktop/tmp/vc/bin/ffmpeg"
SRCDIR=`realpath $1`


if [ ! -d "$SRCDIR" ]; then
    exit "Usage: $0 srcdir [amount]"
fi


RX="^([[:alnum:]]+)-([[:alnum:]]+-)?([[:alnum:]]+)(-[[:digit:]]+-[[:digit:]]+)?.mp4$"
#RX="^([[:alnum:]]+)-([[:alnum:]]+-)?([[:alnum:]]+)(-[0-9]+-[0-9]+)?.mp4$"

for SRCPATH in `ls $SRCDIR/*.mp4`; do
    echo Reversing $FILE ...
    SRCFILE=`basename $SRCPATH`
    [[ "$SRCFILE" =~ $RX ]] \
        && START="${BASH_REMATCH[1]}" \
        && PASS1="${BASH_REMATCH[2]}" \
        && END="${BASH_REMATCH[3]}" \
        && FRAMES="${BASH_REMATCH[4]}"
    echo $SRCFILE : $START / $PASS / $END / $FRAMES

    if [ "$PASS" != "" ]; then
        OUTFILE=$END-r$PASS-$START$FRAMES.mp4 
    else
        OUTFILE=$END-$START$FRAMES.mp4 
    fi

    if [ ! -f "$SRCDIR/$OUTFILE" ]; then
       
        $FFMPEG -i $SRCPATH -vf reverse "$SRCDIR/$OUTFILE"

        echo Created "$SRCDIR/$OUTFILE" .
        echo
    else
        echo Exists: "$SRCDIR/$OUTFILE" .
        echo
    fi
    
done