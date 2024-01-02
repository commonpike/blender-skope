import sys
import bpy
import os
import argparse

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)

import skope

parser = argparse.ArgumentParser(description='Skope runner')
parser.add_argument('--mode', default='edit')
parser.add_argument('--source-dir', default=os.path.dirname(bpy.data.filepath)+'/../render/input/images')
parser.add_argument('--output-dir', default=os.path.dirname(bpy.data.filepath)+'/../render/output')
parser.add_argument('--selected-dir', default=os.path.dirname(bpy.data.filepath)+'/../render/input/states')

args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

scope = skope.KaleidoScope(args.source_dir)
bpy.types.Scene.scope = scope

def main():
  
  print("Skope Runner",args)
  scope.set({
    'output_dir': args.output_dir,
    'selected_dir': args.selected_dir
  })

  if args.mode == "edit-stills":
    # call init_frame on every frame
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(scope.apply_random_state)

  elif args.mode == "generate-thumbs":
    # the command line specified --background --render-anim,
    # which will render the whole animation
    # call init_frame on every frame
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(scope.apply_random_state)
    # call render_* on render events
    bpy.app.handlers.render_init.append(scope.render_init)
    bpy.app.handlers.render_cancel.append(scope.render_cancel)
    bpy.app.handlers.render_complete.append(scope.render_complete)
    
  elif args.mode == "render-stills":
    # this will manually render the files from 
    # the selected dir
    scope.render_stills()

  else:
    # just open the file
    print("edit mode")
  
main()