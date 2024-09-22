#!/bin/sh

BASEDIR=`dirname $0`;
FFMPEG="$HOME/Desktop/tmp/vc/bin/ffmpeg"
OUTDIR=`dirname $1`

function usage() {
	echo Usage: $0 incoming/bla2.mp4 incoming/bla3.mp4 incoming/bla4.mp4 ..
}


LIST=''
FILENAME='concat'
for ((i=1; i<=$#; i++)); do
  	INFILE=${!i}

	if [ ! -f "$INFILE" ]; then
		echo "Infile $INFILE not found; exiting."
		usage;
		exit 1;
	fi

	LIST="$LIST\nfile '$INFILE'" 
	BASENAME=`basename $INFILE`
	FILENAME=$FILENAME-${BASENAME%%.*}

done

FILENAME=`md5 -q -s $FILENAME`

echo $LIST > $OUTDIR/$FILENAME.txt
OUTFILE=$OUTDIR/$FILENAME.mp4

echo Rendering ..
echo Output: $OUTFILE
echo


$FFMPEG -f concat -safe 0 -i "$OUTDIR/$FILENAME.txt" -c copy $OUTFILE




