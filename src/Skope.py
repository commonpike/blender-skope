import bpy
import uuid
import glob
import os


from SkopeState import SkopeState
from SkopeClip import SkopeClip


class Skope:
  """A kaleidoscope for use in blender"""
  

  def __init__(self, input_dir):
  
    print("Kaleidoscope init",input_dir)
    
    # settings 
    self.input_dir = input_dir
    self.output_dir = ''
    self.import_dir = ''
    self.rendering = False
    self.type = 'stills' # stills | clip
    self.scale = 10
    self.image_format = 'PNG'
    self.video_format = 'FFMPEG'
    self.ffmpeg_format = 'MPEG4'
    self.motion_blur = True

    # init state class vars
    scene = bpy.context.scene
    SkopeState.num_frames = scene.frame_end - scene.frame_start # why ?
    
    # current state
    self.state = SkopeState(scene,input_dir)

    # optional clip
    self.clip = None

  def apply(self,scene):
    scene.render.resolution_percentage = self.scale
    filename = str(uuid.uuid4())[:4]
    if self.type == 'stills':
      scene.render.image_settings.file_format = self.image_format
    else:
      scene.render.image_settings.file_format = self.video_format
      scene.render.ffmpeg.format=self.ffmpeg_format
      filename += '-'
    scene.render.filepath = self.output_dir+ '/' + filename
    
    if self.motion_blur:
      scene.render.use_motion_blur = True  
      scene.cycles.motion_blur_position = 'START'  
      scene.render.motion_blur_shutter = 8  
      bpy.ops.render.shutter_curve_preset(shape = 'SHARP')

  def create_random_clip(self, length):
    print("Skope create_random_clip")
    scene = bpy.context.scene
    scene.frame_end = length # +-1 ?
    scene.frame_set(1)
    self.clip = SkopeClip(scene,length)
    self.clip.random()
    self.clip.apply(scene)
  
  def render_stills(self, amount): 
    print("Rendering random stills ..")
    scene = bpy.context.scene
    ofp = scene.render.filepath
    orp = scene.render.resolution_percentage
    oif = scene.render.image_settings.file_format
    scene.render.resolution_percentage = self.scale
    scene.render.image_settings.file_format = self.image_format
    for frame in range(0,amount):
      self.render_still(frame,scene)
    scene.render.filepath = ofp
    scene.render.resolution_percentage = orp
    scene.render.image_settings.file_format = oif
    print("Rendering done.")

  def render_still(self,frame,scene): 
    SkopeState.frame_num = frame
    self.state.random()
    self.state.apply(scene)
    filename = str(frame).zfill(4);
    scene.render.filepath = self.output_dir+ '/' + filename
    print("Rendering",scene.render.filepath)
    bpy.ops.render.render(write_still=True) # render still
    self.state.writeJSON(scene.render.filepath +'.json')

  def render_clip(self,length):
    # create a random clip and step it every frame
    self.create_random_clip(int(length))
    scene = bpy.context.scene
    ofp = scene.render.filepath
    orp = scene.render.resolution_percentage
    oif = scene.render.image_settings.file_format
    scene.render.resolution_percentage = self.scale
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format='MPEG4'
    # scene.render.ffmpeg.codec
    # scene.render.ffmpeg.ffmpeg_preset
    # ...
    
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(self.apply_clip_step)
    filename = str(uuid.uuid4())[:4];
    scene.render.filepath = self.output_dir+ '/' + filename
    
    print("Rendering",scene.render.filepath)
    bpy.ops.render.render(animation=True) # render animation
    #self.clip.writeJSON(scene.render.filepath +'.json')

    scene.render.filepath = ofp
    scene.render.resolution_percentage = orp
    scene.render.image_settings.file_format = oif
    print("Rendering done.")

  # regenerate mode 
  
  def regenerate_stills(self): 
    print("Regenerating selected json files ..")
    state_files=glob.glob(self.import_dir+'/*.json')
    scene = bpy.context.scene
    ofp = scene.render.filepath
    orp = scene.render.resolution_percentage
    scene.render.resolution_percentage = self.scale
    scene.render.image_settings.file_format = self.image_format
    for state_file in state_files:
      self.regenerate_still(state_file,scene)
    scene.render.filepath = ofp
    scene.render.resolution_percentage = orp
    print("Regenerating done.")
    
  def regenerate_still(self,file,scene): 
    basename = os.path.splitext(os.path.basename(file))[0]
    self.state.readJSON(file)
    self.state.apply(scene)
    scene.render.filepath = self.output_dir + '/' + basename
    print("Regenerating",file)
    bpy.ops.render.render(write_still=True) # render still
    self.state.writeJSON(scene.render.filepath+'.json');
    
  # framechange handlers
  # test mode frame_change_pre handler
  
  def apply_random_filepath(self,scene):
    print("apply_random_filepath")
    filename = str(uuid.uuid4())[:4]+'-';
    scene.render.filepath = self.output_dir+ '/' + filename

  def apply_random_state(self,scene,x=0):
    print("apply_random_state")
    #SkopeState.frame_num = scene.frame_current # why ?
    self.state.random()
    self.state.apply(scene)

  def apply_clip_step(self,scene,x=0):
    print("apply_clip_step")
    self.clip.go(scene.frame_current)
    self.clip.apply(scene)
      
