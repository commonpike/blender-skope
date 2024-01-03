#!/bin/sh

#BLENDER=/Applications/UPBGE.app/Contents/MacOS/Blender
BLENDER="${BLENDER:=/Applications/3rdParty/Blender.app/Contents/MacOS/Blender}"

cd `dirname $0`;

COMMAND=${1:-edit} # edit,test,render,regenerate
TYPE=stills # stills, clips
SCALE=10 # percentage
FORMAT=PNG # JPG,PNG
INPUTDIR=render/input/images
OUTPUTDIR=render/output/images
IMPORTDIR=render/input/import

shift # past command

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
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


mkdir -p "$OUTPUTDIR"

if [ ! -d "$INPUTDIR" ]; then
  echo "INPUTDIR $INPUTDIR does not exist"
  exit 1;
fi
if [ ! -d "$IMPORTDIR" ]; then
  echo "IMPORTDIR $IMPORTDIR does not exist"
  exit 1;
fi
if [ ! -f "$BLENDER" ]; then
  echo "Blender is not at $BLENDER"
  exit 1;
fi

case $COMMAND in

    edit)
       $BLENDER ./src/skope.blend \
          --python ./src/skope-init.py -- \
          --mode=edit \
          --input-dir $INPUTDIR \
          --output-dir $OUTPUTDIR \
          --import-dir $IMPORTDIR \
          --format $FORMAT \
          --scale $SCALE
        ;;
        
    test)
        $BLENDER ./src/skope.blend \
          --python ./src/skope-init.py -- \
          --mode=test\
          --input-dir $INPUTDIR \
          --output-dir $OUTPUTDIR \
          --import-dir $IMPORTDIR \
          --format $FORMAT \
          --scale $SCALE
        ;;
        
    render)
        if [ "$TYPE" = "stills" ]; then
          $BLENDER ./src/skope.blend --background \
            --python ./src/skope-init.py \
            --render-anim -- \
            --mode=render \
            --input-dir $INPUTDIR \
            --output-dir $OUTPUTDIR \
            --import-dir $IMPORTDIR \
            --format $FORMAT \
            --scale $SCALE
        elif [ $TYPE = "clips" ]; then
          echo "Render clips: unimplemented" >&2
          exit 1
        else
          echo "Render: unknown type $type" >&2
          exit 1
        fi
        ;;
        
    regenerate)
        if [ "$TYPE" = "stills" ]; then
          $BLENDER ./src/skope.blend --background \
            --python ./src/skope-init.py -- \
            --mode=regenerate \
            --input-dir $INPUTDIR \
            --output-dir $OUTPUTDIR \
            --import-dir $IMPORTDIR \
            --format $FORMAT \
            --scale $SCALE
        elif [ $TYPE = "clips" ]; then
          echo "Render clips: unimplemented" >&2
          exit 1
        else
          echo "Render: unknown type $type" >&2
          exit 1
        fi
        ;;
        
    *)
        # error
        echo 'Unknown command ' $COMMAND >&2
        exit 1
esac



