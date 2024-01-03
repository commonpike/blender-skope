import sys
import bpy
import os
import argparse

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)

import Skope

parser = argparse.ArgumentParser(description='Skope runner')
parser.add_argument('--mode', default='edit')
#parser.add_argument('--type', default='stills')
parser.add_argument('--scale', default='10')
parser.add_argument('--format', default='PNG')
parser.add_argument('--input-dir', default=os.path.dirname(bpy.data.filepath)+'/../render/input/images')
parser.add_argument('--output-dir', default=os.path.dirname(bpy.data.filepath)+'/../render/output')
parser.add_argument('--import-dir', default=os.path.dirname(bpy.data.filepath)+'/../render/input/states')

# read arguments after --
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

skope = Skope.Skope(args.input_dir)
bpy.types.Scene.skope = skope

def main():
  
  print("Skope Runner",args)
  skope.set({
    'output_dir': args.output_dir,
    'import_dir': args.import_dir,
    'image_format': args.format,
    'scale': args.scale
  })

  if args.mode == "test":
    # call apply_random_state on every frame
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(skope.apply_random_state)

  elif args.mode == "render":
    # the command line specified --background --render-anim,
    # which will render the whole animation
    # call init_frame on every frame
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(skope.apply_random_state)
    # call render_* on render events
    bpy.app.handlers.render_init.append(skope.render_init)
    bpy.app.handlers.render_cancel.append(skope.render_cancel)
    bpy.app.handlers.render_complete.append(skope.render_complete)
    
  elif args.mode == "regenerate":
    # this will manually render the files from 
    # the selected dir
    skope.render_stills()

  else:
    # just open the file
    print("edit mode")
  
main()