import bpy
import fnmatch
import glob
import os


from SkopeState import SkopeState
from SkopeMirrors import SkopeMirrors
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
    self.scale = 10
    self.image_format = 'PNG'

    # init state class vars
    scene = bpy.context.scene
    SkopeState.num_frames = scene.frame_end - scene.frame_start
    mirrors = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "mirror*")];
    SkopeMirrors.max_mirrors = len(mirrors)

    # current state
    self.state = SkopeState(input_dir)

    # current clip
    # self.clip = SkopeClip(input_dir)

    self.init_scene(scene)

  def set(self, settings = {}):
    for attr in settings:
      if attr == 'input_dir' : self.input_dir = settings[attr]
      elif attr == 'output_dir' : self.output_dir = settings[attr]
      elif attr == 'import_dir' : self.import_dir = settings[attr]
      elif attr == 'rendering' : self.rendering = settings[attr]
      elif attr == 'scale' : self.scale = int(settings[attr])
      elif attr == 'image_format' : self.image_format = settings[attr]

  def init_scene(self, scene):

    # screen
    screen = scene.objects["screen1"]
    screen.location.y = 10
    
    #mirrors
    mirrors = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "mirror*")];
    for mirror in mirrors:
      mirror.location.y = 0
      mirror.scale.y = 10
    
    # radius
    radius = scene.objects["radius"]
    radius.location.y = -10
    radius.scale.x = self.state.mirrors.inner_radius
    radius.scale.y = self.state.mirrors.inner_radius


  # render mode 
  
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
    
  # test mode frame_change_pre handler
  
  def apply_random_state(self,scene,x=0):
    SkopeState.frame_num = scene.frame_current
    self.state.random()
    self.state.apply(scene)
      
