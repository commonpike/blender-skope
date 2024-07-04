#!/bin/sh

source .env

#BLENDER=/Applications/UPBGE.app/Contents/MacOS/Blender
BLENDER="${BLENDER:=$BLENDER_LOCATION/Blender.app/Contents/MacOS/Blender}"

cd `dirname $0`;

COMMAND=${1:-help} # help, edit,test,render,regenerate
TYPE=stills # stills, clips
SCALE=10 # percentage
AMOUNT=10 #number of stills
LENGTH=360 #number of frames in clip
FORMAT=PNG # JPG,PNG
PROJECTDIR=render/default
INPUTDIR=
OUTPUTDIR=
IMPORTDIR=

shift # past command

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -a|--amount)
      AMOUNT="$2"
      shift # past argument
      shift # past value
      ;;
    -t|--type)
      TYPE="$2"
      shift # past argument
      shift # past value
      ;;
    -s|--scale)
      SCALE="$2"
      shift # past argument
      shift # past value
      ;;
    -f|--format)
      FORMAT="$2"
      shift # past argument
      shift # past value
      ;;
    -p|--project-dir)
      PROJECTDIR="$2"
      shift # past argument
      shift # past value
      ;;
    -i|--input-dir)
      INPUTDIR="$2"
      shift # past argument
      shift # past value
      ;;
    -o|--output-dir)
      OUTPUTDIR="$2"
      shift # past argument
      shift # past value
      ;;
    -d|--import-dir)
      IMPORTDIR="$2"
      shift # past argument
      shift # past value
      ;;
    -l|--length)
      LENGTH="$2"
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done
set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

if [ "$INPUTDIR" = "" ]; then
  INPUTDIR="$PROJECTDIR/input"
else
  PROJECTDIR=`dirname "$INPUTDIR"`
fi
if [ "$OUTPUTDIR" = "" ]; then
  OUTPUTDIR="$PROJECTDIR/output"
fi
if [ "$IMPORTDIR" = "" ]; then
  IMPORTDIR="$PROJECTDIR/import"
fi

if [ ! -d "$INPUTDIR" ]; then
  echo "INPUTDIR $INPUTDIR does not exist"
  exit 1;
fi

mkdir -p "$OUTPUTDIR"
mkdir -p "$IMPORTDIR"

if [ ! -f "$BLENDER" ]; then
  echo "Blender is not at $BLENDER"
  exit 1;
fi

case $COMMAND in

    edit)
       $BLENDER ./src/skope.blend \
          --python ./src/skope-init.py -- \
          --mode edit \
          --input-dir $INPUTDIR \
          --output-dir $OUTPUTDIR \
          --import-dir $IMPORTDIR \
          --format $FORMAT \
          --scale $SCALE
        ;;
        
    test)
        $BLENDER ./src/skope.blend \
          --python ./src/skope-init.py -- \
          --mode test\
          --type $TYPE\
          --input-dir $INPUTDIR \
          --output-dir $OUTPUTDIR \
          --import-dir $IMPORTDIR \
          --format $FORMAT \
          --scale $SCALE
        ;;
        
    render)
        if [ "$TYPE" = "stills" ]; then
          $BLENDER ./src/skope.blend --background \
            --python ./src/skope-init.py -- \
            --mode render \
            --type stills \
            --input-dir $INPUTDIR \
            --output-dir $OUTPUTDIR \
            --import-dir $IMPORTDIR \
            --format $FORMAT \
            --scale $SCALE \
            --amount $AMOUNT
        elif [ $TYPE = "clip" ]; then
          $BLENDER ./src/skope.blend --background \
            --python ./src/skope-init.py -- \
            --mode render \
            --type clip \
            --input-dir $INPUTDIR \
            --output-dir $OUTPUTDIR \
            --import-dir $IMPORTDIR \
            --format $FORMAT \
            --scale $SCALE \
            --length $LENGTH
        else
          echo "Render: unknown type $type" >&2
          exit 1
        fi
        ;;
        
    regenerate)
        if [ "$TYPE" = "stills" ]; then
          $BLENDER ./src/skope.blend --background \
            --python ./src/skope-init.py -- \
            --mode regenerate \
            --input-dir $INPUTDIR \
            --output-dir $OUTPUTDIR \
            --import-dir $IMPORTDIR \
            --format $FORMAT \
            --scale $SCALE
        elif [ $TYPE = "clip" ]; then
          echo "Regenerate clip: unimplemented" >&2
          exit 1
        else
          echo "Regenerate: unknown type $type" >&2
          exit 1
        fi
        ;;
        
    *)
        # help
        echo 'Usage: ' `basename $0` '[command] [arguments] --project-dir render/foobar'
        echo 'Commands: help, test, render, regenerate'
        echo 'Arguments: --amount, --type, --scale, --format, --length'
        echo 'Type: stills (default) or clip'
        echo 'Project dir expects subdirs input, output, import'

        exit 1
esac



