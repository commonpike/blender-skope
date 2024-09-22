#!/bin/sh

source .env

#BLENDER=/Applications/UPBGE.app/Contents/MacOS/Blender
BLENDER="${BLENDER:=$BLENDER_LOCATION}"

cd `dirname $0`;

COMMAND=${1:-help} # help, edit,ui,render,regenerate

if [ ! -f "$BLENDER" ]; then
  echo "Blender is not at $BLENDER"
  exit 1;
fi

case $COMMAND in


    edit | ui)
        $BLENDER ./src/skope.blend \
        --python ./src/skope-init.py -- \
        --command $COMMAND ${@:2}
        break;;

    render | regenerate)
        $BLENDER ./src/skope.blend --background \
        --python ./src/skope-init.py -- \
        --command $COMMAND ${@:2}
        break;;

    *)
        # help
        echo 'Usage: ' `basename $0` '[command] [arguments] --project-dir render/foobar'
        echo 'Commands: help, edit, ui, render, regenerate'
        echo 'Arguments: --amount, --type, --width, --height, --scale, --format, --length'
        echo 'Type: stills (default), clips or loops'
        echo 'Project dir expects subdirs input, output, import'
        break;;
esac
