import sys
import bpy
import os
import argparse

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
   sys.path.append(blend_dir)

import Skope

parser = argparse.ArgumentParser(description='Skope runner')
parser.add_argument('--command', default='edit')
parser.add_argument('--type', default='stills')
parser.add_argument('--width', default='1920')
parser.add_argument('--height', default='1920')
parser.add_argument('--scale', default='20')
parser.add_argument('--format', default='PNG')
parser.add_argument('--amount', default='10')
parser.add_argument('--length', default='360')
parser.add_argument('--project-dir', default=os.path.dirname(bpy.data.filepath)+'/../render/default')
parser.add_argument('--input-dir', default='')
parser.add_argument('--output-dir', default='')
parser.add_argument('--import-dir', default='')

# read arguments after --
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

# guess more sensible defaults 
if args.input_dir:
    args.project_dir = os.path.dirname(args.input_dir)
elif args.output_dir:
    args.project_dir = os.path.dirname(args.output_dir)
elif args.import_dir:
    args.project_dir = os.path.dirname(args.import_dir)
    
if not os.path.isdir(args.project_dir):
  bpy.ops.wm.quit_blender()
  raise Exception("--project-dir "+args.project_dir+" does not exist")

if not args.input_dir:
  args.input_dir = args.project_dir+'/input'
if not args.output_dir:
  args.output_dir = args.project_dir+'/output'
if not args.import_dir:
  args.import_dir = args.project_dir+'/import'

# check if dirs exist

if not os.path.isdir(args.input_dir):
  bpy.ops.wm.quit_blender()
  raise Exception("--input-dir "+args.input_dir+" does not exist")
if not os.path.exists(args.output_dir):
  os.makedirs(args.output_dir)
elif not os.path.isdir(args.output_dir):
  bpy.ops.wm.quit_blender()
  raise Exception("--output-dir "+args.output_dir+" is not a directory")
if not os.path.exists(args.output_dir):
  os.makedirs(args.output_dir)
elif not os.path.isdir(args.import_dir):
  bpy.ops.wm.quit_blender()
  raise Exception("--import-dir "+args.import_dir+" is not a directory")

skope = Skope.Skope(args.input_dir)
# skope.__init__ does this 
# bpy.types.Scene.skope = skope

def main():

  print("skope-init",args)
  skope.settings.fixed['output_dir'] = args.output_dir
  skope.settings.fixed['import_dir'] = args.import_dir
  skope.settings.fixed['image_format'] = args.format
  skope.settings.fixed['length'] = int(args.length)
  skope.settings.fixed['width'] = int(args.width)
  skope.settings.fixed['height'] = int(args.height)
  skope.settings.fixed['scale'] = int(args.scale)
  skope.type = args.type
  skope.applyFixedSettings()

  if args.command == "ui":
    
    bpy.app.handlers.render_init.append(skope.apply_start_render)
    bpy.app.handlers.render_cancel.append(skope.apply_stop_render)
    bpy.app.handlers.render_complete.append(skope.apply_stop_render)
    
    skope.registerUIPanels()
    skope.initUI()

    if args.type == "stills":
      # call apply_random_state on every frame
      bpy.app.handlers.frame_change_pre.clear()
      bpy.app.handlers.frame_change_pre.append(skope.apply_random_state)
      # but not if you render one frame
      bpy.app.handlers.render_pre.clear()
      bpy.app.handlers.render_pre.append(skope.freeze)
      bpy.app.handlers.render_post.clear()
      bpy.app.handlers.render_post.append(skope.unfreeze)
    elif args.type == "clips":
      # create a random clip and step it every frame
      skope.create_random_clip(int(args.length))
      bpy.app.handlers.frame_change_pre.clear()
      bpy.app.handlers.frame_change_pre.append(skope.apply_clip_step)
      #bpy.app.handlers.render_pre.append(skope.apply_random_filepath)

    else:
      raise Exception("Type "+args.type+" not supported")
    
  elif args.command == "render":
    if args.type == "stills":
      skope.render_stills(int(args.amount))
    elif args.type == "clips":
      skope.render_clips(int(args.length),int(args.amount))
    elif args.type == "loops":
      skope.render_loops(int(args.length),int(args.amount))
    else:
      raise Exception("Type "+args.type+" not supported")
    
  elif args.command == "regenerate":
    # this will manually regenerate stills based on
    # the state files from  the import dir
    if args.type == "stills":
      skope.regenerate_stills()
    elif args.type == "clips":
      bpy.app.handlers.frame_change_pre.clear()
      bpy.app.handlers.frame_change_pre.append(skope.apply_clip_step)
      skope.regenerate_clips(int(args.length))


  else:
    # just open the file
    print("edit command")
  
main()