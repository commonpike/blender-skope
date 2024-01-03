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



  # regenerate mode 
  
  def render_stills(self): 
    print("Rendering selected json files ..")
    state_files=glob.glob(self.import_dir+'/*.json')
    scene = bpy.context.scene
    ofp = scene.render.filepath
    orp = scene.render.resolution_percentage
    scene.render.resolution_percentage = self.scale
    scene.render.image_settings.file_format = self.image_format
    for state_file in state_files:
      self.render_still(state_file,scene)
    scene.render.filepath = ofp
    scene.render.resolution_percentage = orp
    print("Rendering done.")
    
  def render_still(self,file,scene): 
    basename = os.path.splitext(os.path.basename(file))[0]
    self.state.readJSON(file)
    self.state.apply(scene)
    scene.render.filepath = self.output_dir + '/' + basename
    print("Rendering",file)
    bpy.ops.render.render(write_still=True) # render still
    self.state.writeJSON(scene.render.filepath+'.json');
    
  # render mode
  
  def apply_random_state(self,scene,x=0):
    
    SkopeState.frame_num = scene.frame_current
    self.state.random()
    self.state.apply(scene)
    if self.rendering:
      scene.render.filepath = self.output_dir+ '/'
      print("Generating",scene.render.filepath)
      scene.render.resolution_percentage = self.scale
      filename = str(scene.frame_current).zfill(4);
      self.state.writeJSON(scene.render.filepath+filename +'.json')
        
  def render_init(self,scene,x):
    print('Rendering started');
    self.rendering = True

  def render_cancel(self,scene,x):
    print('Rendering canceled');
    self.rendering = False
      
  def render_complete(self,scene,x):
    print('Rendering complete');
    self.rendering = False
  
