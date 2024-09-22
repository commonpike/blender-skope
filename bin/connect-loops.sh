#!/bin/bash

# output a script to 
# randonly connect loops based on the 
# filename pattern skope uses

BASEDIR=`dirname $0`;
FFMPEG="$HOME/Desktop/tmp/vc/bin/ffmpeg"
SRCDIR=`realpath $1`
REQAMOUNT=$2
NEWLINE=$'\n'
TAB=$'\t'
CMD="../../../bin/concat.sh"

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

echo "#!/bin/bash"
echo 'cd `dirname $0`'
echo

for ((run = 1; run <= $AMOUNT ; run++ )); do
    echo "# Run $run ..."
    CONCAT=""
    USED=""
    
    RNDPATH=`ls $SRCDIR/*-*.mp4 2> /dev/null |sort -R | tail -1`
    RNDHEAD=`basename $RNDPATH`
    USED="$RNDHEAD"

    for ((i = 1; i <= $AMOUNT ; i++ )); do
        [[ "$RNDHEAD" =~ $RX ]] && START="${BASH_REMATCH[1]}" && PASS1="${BASH_REMATCH[2]}" && MID="${BASH_REMATCH[4]}"
        #echo $RNDHEAD : $START / $PASS1 / $MID

        RNDPATH=`ls $SRCDIR/$MID-*.mp4 2> /dev/null |sort -R | tail -1`
        
        if [ "" != "$RNDPATH" ]; then
            RNDTAIL=`basename $RNDPATH`
            if [[ $USED == *"$RNDTAIL"* ]]; then
                continue
            fi
            USED="$USED $RNDTAIL"
            [[ "$RNDTAIL" =~ $RX ]] && PASS2="${BASH_REMATCH[2]}" && END="${BASH_REMATCH[4]}"
            #echo $RNDTAIL: $MID / $PASS2 / $END

            CONCAT="$CONCAT\\$NEWLINE$TAB$RNDHEAD "
            RNDHEAD=$RNDTAIL
            
        else
            echo "# Stuck on $i";
            CONCAT="$CONCAT\\$NEWLINE$TAB$RNDHEAD "
            echo "# Used" `wc -w <<< "$USED"`
            echo "$CMD $CONCAT"
            echo
            break
        fi
    done
    CONCAT="$CONCAT\\$NEWLINE$TAB$RNDHEAD "
    echo "# Stopped on $i";
    echo "# Used" `wc -w <<< "$USED"`
    echo "$CMD $CONCAT"
    echo
done