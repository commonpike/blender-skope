import bpy
import math
import random
import fnmatch
import json
import glob
import os

PI=math.pi
TWO_PI=2*math.pi

class KaleidoScopeMirror:
  def __init__(self):
    self.location = {"x":0, "y":0, "z":0 }
    self.rotation = {"x":0, "y":0, "z":0 }
    self.hide = False
   
class KaleidoScopeCamera:
  def __init__(self):
    self.location = {"x":0, "y":0, "z":0 }
    #self.rotation: {"x":0, "y":0, "z":0 }
    
class KaleidoScopeScreen:
  def __init__(self):
    self.rotation = {"x":0, "y":0, "z":0 }
    self.location = {"x":0, "y":0, "z":0 }
    self.scale = {"x":0, "y":0 }
    self.image1 = ""
    self.image2 = ""
    self.mix = .5
    
class KaleidoScopeState:

  frame_num=0
  max_mirros=8
  num_frames=360
  src_globs=['*.JPG','*.PNG']

  def __init__(self,source_dir):
    self.source_dir=source_dir
    self.images = []
    for pattern in self.src_globs:
      self.images.extend(glob.glob(source_dir+'/'+pattern.upper()))
      self.images.extend(glob.glob(source_dir+'/'+pattern.lower()))
    #print(self.images)
    self.num_mirrors=5
    self.inner_radius=4
    self.mirror_shift=.5
    self.mirror_wiggle=1/5 # 1 = 100%
    self.screen_scale=60
    self.camera = KaleidoScopeCamera()
    self.screen = KaleidoScopeScreen()
    self.mirrors = []

    KaleidoScopeState.frame_num = bpy.context.scene.frame_current
    
    for n in range(KaleidoScopeState.max_mirrors):
      self.mirrors.append(KaleidoScopeMirror())
    self.readScene(bpy.context.scene)
  
    
  def set(self, settings = {}):
    for attr in settings:
      if attr == 'num_mirrors' : self.num_mirrors = settings[attr]
      if attr == 'inner_radius' : self.inner_radius = settings[attr]
      if attr == 'mirror_shift' : self.mirror_shift = settings[attr]
      if attr == 'mirror_wiggle' : self.mirror_wiggle = settings[attr]
      if attr == 'screen_scale' : self.screen_scale = settings[attr]

  def readScene(self,scene):
    print("Read state")
    
    # screen
    screen = scene.objects["screen1"]
    self.screen.location["x"] = screen.location.x
    self.screen.location["y"] = screen.location.y
    self.screen.location["z"] = screen.location.z
    self.screen.rotation["x"] = screen.rotation_euler.x
    self.screen.rotation["y"] = screen.rotation_euler.y
    self.screen.rotation["z"] = screen.rotation_euler.z
    self.screen.scale["x"] = screen.scale[0]
    self.screen.scale["y"] = screen.scale[1]
    
    # camera
    camera = scene.objects["camera"]
    self.camera.location["x"] = camera.location.x
    self.camera.location["y"] = camera.location.y
    self.camera.location["z"] = camera.location.z
    
    # mirrors
    for n in range(self.num_mirrors):
      mirror = scene.objects["mirror"+str(n+1)]
      self.mirrors[n].location["x"] = mirror.location.x
      self.mirrors[n].location["y"] = mirror.location.y
      self.mirrors[n].location["z"] = mirror.location.z
      self.mirrors[n].rotation["x"] = mirror.rotation_euler.x
      self.mirrors[n].rotation["y"] = mirror.rotation_euler.y
      self.mirrors[n].rotation["z"] = mirror.rotation_euler.z
      self.mirrors[n].hide = mirror.hide_viewport

  def default_mirror_angle(self,n):
    global TWO_PI
    return (n+self.mirror_shift)*TWO_PI/self.num_mirrors - PI

  def default_mirror_center(self,n):
    a = self.default_mirror_angle(n)
    x = self.inner_radius*math.sin(a)
    y = self.inner_radius*math.cos(a)
    return x,y
    
  def reset(self,num_mirrors=3):
    self.reset_screen()
    self.reset_camera()
    self.reset_mirrors(num_mirrors,0)
    
  def randomize(self):
    self.random_screen()
    self.random_camera()
    self.random_mirrors()

  def reset_screen(self):
    print("Reset screen")
    self.screen.rotation["y"] = 0
    self.screen.scale["x"] = self.screen_scale / 2
    self.screen.scale["y"] = self.screen_scale / 2
    self.screen.image1 = random.choice(self.images)
    self.screen.image2 = random.choice(self.images)
    self.screen.mix = .5

  def random_screen(self):
    global TWO_PI
    print("Prepare screen")
    self.reset_screen()
    self.screen.rotation["y"] = TWO_PI*KaleidoScopeState.frame_num/KaleidoScopeState.num_frames
    scale = 2 * self.inner_radius + random.random() * self.screen_scale
    self.screen.scale["x"] = scale
    self.screen.scale["y"] = scale
    self.screen.image1 = random.choice(self.images)
    self.screen.image2 = random.choice(self.images)
    self.screen.mix =random.random()
    
  def reset_camera(self):
    print("Reset camera")
    self.camera.location["x"] = 0
    self.camera.location["z"] = 0

  def random_camera(self):
    print("Prepare camera")
    self.reset_camera()
    self.camera.location["x"] = (random.random()-.5)*self.inner_radius
    self.camera.location["z"] = (random.random()-.5)*self.inner_radius
    
  def reset_mirrors(self, num_mirrors=3, mirror_shift=0):
    print("Reset mirrors", num_mirrors, mirror_shift)
    
    self.num_mirrors = num_mirrors
    self.mirror_shift= mirror_shift
    
    for n in range(self.num_mirrors):
        mirror = self.mirrors[n]
        a=self.default_mirror_angle(n)
        x,z=self.default_mirror_center(n)
        #print('show mirror ',mirror,a,x,z)
        mirror.rotation["y"]=a
        mirror.location["x"]=x
        mirror.location["y"]=0
        mirror.location["z"]=z
        mirror.hide=False
        
    for n in range(self.num_mirrors,len(self.mirrors)):
        print('hide mirror ',mirror)
        mirror = self.mirrors[n]
        mirror.hide=True

  def random_mirrors(self):
    global TWO_PI
    
    print("Prepare mirrors")

    self.reset_mirrors(
      random.randint(3, len(self.mirrors)),
      KaleidoScopeState.frame_num/KaleidoScopeState.num_frames
    )
    for n in range(self.num_mirrors):
        print('wiggle ',n)
        mirror = self.mirrors[n]
        mirror.rotation["y"] += random.random()*TWO_PI*self.mirror_wiggle
  
  

  def apply(self,scene):
    print("Apply state")
    
    # screen
    screen = scene.objects["screen1"]
    screen.rotation_euler.x = self.screen.rotation["x"]
    screen.rotation_euler.y = self.screen.rotation["y"]
    screen.rotation_euler.z = self.screen.rotation["z"]
    screen.location.x = self.screen.location["x"]
    screen.location.y = self.screen.location["y"]
    screen.location.z = self.screen.location["z"]
    screen.scale[0] = self.screen.scale["x"]
    screen.scale[1] = self.screen.scale["y"]
    bpy.data.images['source1'].filepath = self.screen.image1
    bpy.data.images['source2'].filepath = self.screen.image2
    bpy.data.materials['image'].node_tree.nodes["Mix Shader"].inputs[0].default_value=self.screen.mix
    
    # camera
    camera = scene.objects["camera"]
    camera.location.x = self.camera.location["x"]
    camera.location.y = self.camera.location["y"]
    camera.location.z = self.camera.location["z"]
    
    # mirrors
    for n in range(self.max_mirrors):
      mirror = scene.objects["mirror"+str(n+1)]
      #print(mirror,self.mirrors[n])
      mirror.location.x = self.mirrors[n].location["x"]
      mirror.location.y = self.mirrors[n].location["y"]
      mirror.location.z = self.mirrors[n].location["z"]
      mirror.rotation_euler.x = self.mirrors[n].rotation["x"]
      mirror.rotation_euler.y = self.mirrors[n].rotation["y"]
      mirror.rotation_euler.z = self.mirrors[n].rotation["z"]
      mirror.hide_viewport = self.mirrors[n].hide
      mirror.hide_render = self.mirrors[n].hide

    # render
    # https://docs.blender.org/api/blender2.8/bpy.ops.render.html#bpy.ops.render.render
    
  def setKeyFrame(self,scene,frame):
    print("setKeyFrame",frame)
    
    # screen
    screen = scene.objects["screen1"]
    screen.keyframe_insert(data_path="rotation_euler",index=-1, frame=frame)
    screen.keyframe_insert(data_path="location",index= -1, frame=frame)
    screen.keyframe_insert(data_path="scale",index= -1, frame=frame)
    
    # TODO images
    # ...
    # bpy.data.images['source1'].filepath = self.screen.image1
    # bpy.data.images['source2'].filepath = self.screen.image2
    # bpy.data.materials['image'].node_tree.nodes["Mix Shader"].inputs[0].default_value=self.screen.mix
    
    # camera
    camera = scene.objects["camera"]
    camera.keyframe_insert(data_path="location",index=-1, frame=frame)
    
    # mirrors
    mirrors = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "mirror*")];
    for mirror in mirrors:
      mirror.keyframe_insert(data_path="location",index=-1, frame=frame)
      mirror.keyframe_insert(data_path="rotation_euler",index=-1, frame=frame)
      mirror.keyframe_insert(data_path="hide_viewport",index=-1, frame=frame)
      mirror.keyframe_insert(data_path="hide_render",index=-1, frame=frame)
          
    # TODO easing, interpolation ...
    # https://blender.stackexchange.com/questions/260149/set-keyframe-interpolation-constant-while-setting-a-keyframe-in-blender-python
    # https://docs.blender.org/api/current/bpy.types.Keyframe.html


  def writeJSON(self,file):
    print("Write json", file)
    with open(file, "w") as outfile:
      outfile.write(json.dumps(self,default=vars,indent=4))
    
  def readJSON(self,file):
    print("Read json", file)
    with open(file, "r") as infile:
      data = json.load(infile)
      self.fromJSON(data)

  def toJSON(self):
    return json.dumps(self,default=vars,indent=4)

  def fromJSON(self,data):
    # self
    self.num_mirrors = data["num_mirrors"]
    self.inner_radius = data["inner_radius"]
    self.mirror_shift = data["mirror_shift"]
    
    # screen
    self.screen.location["x"] = data["screen"]["location"]["x"]
    self.screen.location["y"] = data["screen"]["location"]["y"]
    self.screen.location["z"] = data["screen"]["location"]["z"]
    self.screen.rotation["x"] = data["screen"]["rotation"]["x"]
    self.screen.rotation["y"] = data["screen"]["rotation"]["y"]
    self.screen.scale["x"] = data["screen"]["scale"]["x"]
    self.screen.scale["y"] = data["screen"]["scale"]["y"]
    self.screen.rotation["z"] = data["screen"]["rotation"]["z"]
    self.screen.image1 = data["screen"]["image1"]
    self.screen.image2 = data["screen"]["image2"]
    self.screen.mix = data["screen"]["mix"]
  
    # camera
    self.camera.location["x"] = data["camera"]["location"]["x"]
    self.camera.location["y"] = data["camera"]["location"]["y"]
    self.camera.location["z"] = data["camera"]["location"]["z"]
  
    # mirrors
    for n in range(len(data["mirrors"])):
      self.mirrors[n].location["x"] = data["mirrors"][n]["location"]["x"]
      self.mirrors[n].location["y"] = data["mirrors"][n]["location"]["y"]
      self.mirrors[n].location["z"] = data["mirrors"][n]["location"]["z"]
      self.mirrors[n].rotation["x"] = data["mirrors"][n]["rotation"]["x"]
      self.mirrors[n].rotation["y"] = data["mirrors"][n]["rotation"]["y"]
      self.mirrors[n].rotation["z"] = data["mirrors"][n]["rotation"]["z"]
      self.mirrors[n].hide = data["mirrors"][n]["hide"]
    
    #print(json.dumps(self,default=vars,indent=4))

      
class KaleidoScopeClip:
  
  interpolation = 'BEZIER'
  
  def __init__(self,source_dir):
    self.start = KaleidoScopeState(source_dir)
    self.end = KaleidoScopeState(source_dir)
    
  def set(self, settings = {}):
    for attr in settings:
      if attr == 'interpolation' : KaleidoScopeClip.interpolation = settings[attr]

  def randomizeStart(self,scene):
    self.start.randomize()
    self.start.apply(scene)
    self.start.setKeyFrame(scene,scene.frame_start)

  def randomizeEnd(self,scene):
    self.end.randomize()
    self.end.apply(scene)
    self.end.setKeyFrame(scene,scene.frame_end)

  def randomize(self,scene):
    self.randomizeStart(scene)
    self.randomizeEnd(scene)

  def reset(self,scene):
    self.start.readScene(scene)
    self.start.setKeyFrame(scene,scene.frame_start)
    self.start.readScene(scene)
    self.start.setKeyFrame(scene,scene.frame_end)
    
class KaleidoScope:
  """A kaleidoscope for use in blender"""
  

  def __init__(self, source_dir):
  
    print("Kaleidoscope init",source_dir)
    
    # settings 
    self.source_dir = source_dir
    self.output_dir = ''
    self.selected_dir = ''
    self.rendering = False
    self.thumb_scale = 10
    self.large_scale = 200
    self.image_format = 'PNG'

    # init state class vars
    scene = bpy.context.scene
    KaleidoScopeState.num_frames = scene.frame_end - scene.frame_start
    mirrors = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, "mirror*")];
    KaleidoScopeState.max_mirrors = len(mirrors)

    # current state
    self.state = KaleidoScopeState(source_dir)

    # current clip
    self.clip = KaleidoScopeClip(source_dir)

    self.init_scene(scene)

  def set(self, settings = {}):
    for attr in settings:
      if attr == 'source_dir' : self.source_dir = settings[attr]
      elif attr == 'output_dir' : self.output_dir = settings[attr]
      elif attr == 'selected_dir' : self.selected_dir = settings[attr]
      elif attr == 'rendering' : self.rendering = settings[attr]
      elif attr == 'thumb_scale' : self.thumb_scale = settings[attr]
      elif attr == 'large_scale' : self.large_scale = settings[attr]
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
    radius.scale.x = self.state.inner_radius
    radius.scale.y = self.state.inner_radius



  # render mode 
  
  def render_stills(self): 
    print("Rendering selected json files ..")
    state_files=glob.glob(self.selected_dir+'/*.json')
    scene = bpy.context.scene
    ofp = scene.render.filepath
    orp = scene.render.resolution_percentage
    scene.render.resolution_percentage = self.large_scale
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
    
  # generate mode
  
  def apply_random_state(self,scene,x=0):
    
    KaleidoScopeState.frame_num = scene.frame_current
    self.state.randomize()
    self.state.apply(scene)
    if self.rendering:
      scene.render.filepath = self.output_dir+ '/'
      print("Generating",scene.render.filepath)
      scene.render.resolution_percentage = self.thumb_scale
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
  
