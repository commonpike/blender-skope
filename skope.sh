#!/bin/sh

source .env

#BLENDER=/Applications/UPBGE.app/Contents/MacOS/Blender
BLENDER="${BLENDER:=$BLENDER_LOCATION}"

cd `dirname $0`;

COMMAND=${1:-help} # help, edit,ui,render,regenerate
TYPE=stills # stills, clips
WIDTH=1920 # pixels
HEIGHT=1920 # pixels
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
    -w|--width)
      WIDTH="$2"
      shift # past argument
      shift # past value
      ;;
    -h|--height)
      HEIGHT="$2"
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
  images=`find $PROJECTDIR -type f -exec file --mime-type {} \+ | awk -F: '{if ($2 ~/image\//) print $1}'`
  if [ "$images" != "" ]; then
    echo found $images ..
    read -p "Move these files to $PROJECTDIR/input [Y/n]? " -n 1 -r
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
      mkdir $PROJECTDIR/input
      mv $images $PROJECTDIR/input
    else
      exit;
    fi
  else
    exit;
  fi
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
          --width $WIDTH \
          --height $HEIGHT \
          --scale $SCALE
        ;;
        
    ui)
        $BLENDER ./src/skope.blend \
          --python ./src/skope-init.py -- \
          --mode ui\
          --type $TYPE\
          --input-dir $INPUTDIR \
          --output-dir $OUTPUTDIR \
          --import-dir $IMPORTDIR \
          --format $FORMAT \
          --width $WIDTH \
          --height $HEIGHT \
          --scale $SCALE \
          --length $LENGTH
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
            --width $WIDTH \
            --height $HEIGHT \
            --scale $SCALE \
            --amount $AMOUNT
        elif [ $TYPE = "clips" ]; then
          $BLENDER ./src/skope.blend --background \
            --python ./src/skope-init.py -- \
            --mode render \
            --type clip \
            --input-dir $INPUTDIR \
            --output-dir $OUTPUTDIR \
            --import-dir $IMPORTDIR \
            --format $FORMAT \
            --width $WIDTH \
            --height $HEIGHT \
            --scale $SCALE \
            --length $LENGTH \
            --amount $AMOUNT
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
            --width $WIDTH \
            --height $HEIGHT \
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
        echo 'Commands: help, edit, ui, render, regenerate'
        echo 'Arguments: --amount, --type, --width, --height, --scale, --format, --length'
        echo 'Type: stills (default) or clips'
        echo 'Project dir expects subdirs input, output, import'

        exit 1
esac



