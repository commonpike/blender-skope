#!/bin/sh

#BLENDER=/Applications/UPBGE.app/Contents/MacOS/Blender
BLENDER="${BLENDER:=/Applications/3rdParty/Blender.app/Contents/MacOS/Blender}"

cd `dirname $0`;

mkdir -p ./render/output/thumbs/
mkdir -p ./render/output/stills/
mkdir -p ./render/input/states/

select mode in edit edit-stills generate-thumbs render-stills; do
    case $mode in
        generate-thumbs) 
            $BLENDER ./src/skope.blend --background \
                --python ./src/skope-init.py \
                --render-anim -- \
                --mode=generate-thumbs \
                --source-dir ./render/input/images/ \
                --output-dir ./render/output/thumbs/
            break ;;
        render-stills) 
            $BLENDER ./src/skope.blend --background \
                --python ./src/skope-init.py -- \
                --mode=render-stills \
                --source-dir ./render/input/images/ \
                --selected-dir ./render/input/states/ \
                --output-dir ./render/output/stills/
            break ;;
        edit-stills) 
            $BLENDER ./src/skope.blend \
                --python ./src/skope-init.py -- \
                --mode=edit-stills
            break;;
        *) 
            $BLENDER ./src/skope.blend \
                --python ./src/skope-init.py -- \
                --mode=edit
            break;;
   esac
done

