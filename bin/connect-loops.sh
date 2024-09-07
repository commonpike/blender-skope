#!/bin/bash

BASEDIR=`dirname $0`;
FFMPEG="$HOME/Desktop/tmp/vc/bin/ffmpeg"
SRCDIR=`realpath $1`
REQAMOUNT=$2

if [ ! -d "$SRCDIR" ]; then
    exit "Usage: $0 srcdir [amount]"
fi
if [ "$REQAMOUNT" = "" ]; then
    AMOUNT=1
else
    AMOUNT=$(($REQAMOUNT))
fi

#RX="^([[:alnum:]]+)-([[:alnum:]]+-)?([[:alnum:]]+)(-[[:digit:]]+-[[:digit:]]+)?.mp4$"
RX="^([[:alnum:]]+)-(([[:alnum:]]+-)*)([[:alnum:]]+)(-[[:digit:]]+-[[:digit:]]+).mp4$"

for ((i = 1; i <= $AMOUNT ; i++ )); do
    echo Run $i ...
    RNDPATH=`ls $SRCDIR/*-*.mp4 |sort -R | tail -1`
    RNDHEAD=`basename $RNDPATH`
    [[ "$RNDHEAD" =~ $RX ]] && START="${BASH_REMATCH[1]}" && PASS1="${BASH_REMATCH[2]}" && MID="${BASH_REMATCH[4]}"
    echo $RNDHEAD : $START / $PASS1 / $MID

    RNDPATH=`ls $SRCDIR/$MID-*.mp4 |sort -R | tail -1`
    if [ "" != "$RNDPATH" ]; then
        RNDTAIL=`basename $RNDPATH`
        [[ "$RNDTAIL" =~ $RX ]] && PASS2="${BASH_REMATCH[2]}" && END="${BASH_REMATCH[4]}"
        echo $RNDTAIL: $MID / $PASS2 / $END

        OUTFILE=$START-$PASS1$MID-$PASS2$END-0000-9999.mp4 

        if [ ! -f "$SRCDIR/$OUTFILE" ]; then
            echo "Concat $RNDHEAD - $RNDTAIL => $OUTFILE"

            echo "file '$SRCDIR/$RNDHEAD'" > $SRCDIR/concat.tmp
            echo "file '$SRCDIR/$RNDTAIL'" >> $SRCDIR/concat.tmp

            $FFMPEG -f concat -safe 0 -i $SRCDIR/concat.tmp -c copy "$SRCDIR/$OUTFILE"

            echo Created "$SRCDIR/$OUTFILE" .
            echo
        else
            echo Exists: "$SRCDIR/$OUTFILE" .
            echo
        fi
    else
        echo Stuck: "$SRCDIR/$OUTFILE" .
        echo
    fi
done