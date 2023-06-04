#!/bin/sh

#BLENDER=/Applications/UPBGE.app/Contents/MacOS/Blender
BLENDER=/Applications/3rdParty/Blender.app/Contents/MacOS/Blender

cd `dirname $0`;

mkdir -p ./output/thumbs/
mkdir -p ./output/selected/
mkdir -p ./output/stills/

select mode in edit edit-stills generate-thumbs render-stills; do
    case $mode in
        generate-thumbs) 
            $BLENDER ./kaleidogen.blend --background \
                --python ./runner.py \
                --render-anim -- \
                --mode=generate-thumbs \
                --source-dir ./source/ \
                --thumbs-dir ./output/thumbs/
            break ;;
        render-stills) 
            $BLENDER ./kaleidogen.blend --background \
                --python ./runner.py -- \
                --mode=render-stills \
                --source-dir ./source/ \
                --selected-dir ./output/selected/ \
                --large-dir ./output/stills/
            break ;;
        edit-stills) 
            $BLENDER ./kaleidogen.blend \
                --python ./runner.py -- \
                --mode=edit-stills
            break;;
        *) 
            $BLENDER ./kaleidogen.blend \
                --python ./runner.py -- \
                --mode=edit
            break;;
   esac
done

