import sys
import bpy
import os
import argparse

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)

import kaleidogen

parser = argparse.ArgumentParser(description='Kaleidoscope runner')
parser.add_argument('--mode', default='edit')
parser.add_argument('--source-dir', default=os.path.dirname(bpy.data.filepath)+'/source')
parser.add_argument('--thumbs-dir', default=os.path.dirname(bpy.data.filepath)+'/output/thumbs')
parser.add_argument('--selected-dir', default=os.path.dirname(bpy.data.filepath)+'/output/selected')
parser.add_argument('--stills-dir', default=os.path.dirname(bpy.data.filepath)+'/output/large')

args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

def main():
  
  print("Kaleidogen Runner",args)
  kscope = kaleidogen.KaleidoScope(args.source_dir)
  kscope.settings.set({
    'thumbs_dir': args.thumbs_dir,
    'selected_dir': args.selected_dir,
    'stills_dir': args.stills__dir
  })

  if args.mode == "edit-stills":
    # call init_frame on every frame
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(kscope.init_frame)

  elif args.mode == "generate-thumbs":
    # the command line specified --background --render-anim,
    # which will render the whole animation
    # call init_frame on every frame
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(kscope.init_frame)
    # call render_* on render events
    bpy.app.handlers.render_init.append(kscope.render_init)
    bpy.app.handlers.render_cancel.append(kscope.render_cancel)
    bpy.app.handlers.render_complete.append(kscope.render_complete)
    
  elif args.mode == "render-stills":
    # this will manually render the files from 
    # the selected dir
    kscope.render()

  else:
    # just open the file
    print("edit mode")
  
main()