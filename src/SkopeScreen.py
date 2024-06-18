import bpy
import random
import glob
import math

from easings import mix, rnd
from utilities import dict2obj

PI=math.pi
TWO_PI=2*math.pi

class SkopeScreen:

  settings = dict2obj({

    "fix_roughness": 0,
    
    "rnd_img1": True,
    "rnd_img2": True,

    "src_dir": '',
    "src_globs": ['*.JPG','*.PNG'],
    "def_width": 10.0,
    "def_height":10.0,
    "def_dist": 0.0,
    "def_location": {"x":0, "y":0, "z":0 },
    "def_rotation": {"x":0, "y":0, "z":0 },

    "rnd_scale" : True,
    "def_scale": {"x":1,"y":1},
    "min_scale" : .5,
    "max_scale": 2,
    "dist_scale": "LINEAR",

    "rnd_fade": True,
    "def_fade": .5,
    "min_fade": 0,
    "max_fade": 1,
    "dist_fade": "LINEAR",

    "rnd_rotz": True,
    "def_rotz": 0,
    "min_rotz": 0,
    "max_rotz": TWO_PI,
    "dist_rotz": "LINEAR"

  })

  def __init__(self,scene=None,inputdir=None):

    self.settings.src_dir = inputdir
    self.reset();

    if scene:
      screen = scene.objects.get("screen")
      if screen:
        raise Exception("Sorry, only one SkopeScreen per scene")
      else:
        self.create(scene)
    else:
      print("Skopescreen off-scene")
      self.object = None
      self.material = None
      self.fader = None
      self.sources = []
        
    if scene:
      self.apply(scene)


  def reset(self):
    print("Skopescreen reset")

    self.width = self.settings.def_width
    self.height = self.settings.def_height
    self.location = self.settings.def_location
    self.rotation = self.settings.def_rotation
    self.scale = self.settings.def_scale
    self.fade = self.settings.def_fade
    self.dist = self.settings.def_dist
    self.images = []
    if self.settings.src_dir:
      for pattern in self.settings.src_globs:
        self.images.extend(glob.glob(self.settings.src_dir+'/'+pattern.upper()))
        self.images.extend(glob.glob(self.settings.src_dir+'/'+pattern.lower()))
    if len(self.images):
      self.image1 = self.images[0]
    if len(self.images) > 1:
      self.image2 = self.images[1]

  def create(self,scene):
    print("SkopeScreen create")

    vert = [
        (-self.width/2, -self.height/2, self.dist), 
        (self.width/2, -self.height/2, self.dist), 
        (-self.width/2, self.height/2, self.dist), 
        (self.width/2, self.height/2, self.dist)
    ]
    fac = [(0, 1, 3, 2)]
    screen_data = bpy.data.meshes.new("screen")
    screen_data.from_pydata(vert, [], fac)
    screen_data.uv_layers.new(name='ScreenUVMap')
    self.object = bpy.data.objects.new("screen", screen_data)

    self.material = bpy.data.materials.new(name = "ScreenMaterial")
    self.material.roughness = self.settings.fix_roughness
    self.material.use_nodes = True
    self.material.node_tree.nodes.clear()
    
    material = self.material.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    material.location.x = 600
    material.location.y = 200
    
    self.fader = self.material.node_tree.nodes.new(type="ShaderNodeMixShader")
    self.fader.location.x = 400
    self.fader.location.y = 200
    
    self.sources = []

    image1 = self.material.node_tree.nodes.new(type="ShaderNodeTexImage")
    image1.location.x = 0
    image1.location.y = 200

    self.image1 = random.choice(self.images)
    bpy.ops.image.new(name='ScreenSource1')
    source1 = bpy.data.images['ScreenSource1']
    source1.source = 'FILE'
    source1.filepath = self.image1
    image1.image = source1
    self.sources.append(source1)

    image2 = self.material.node_tree.nodes.new(type="ShaderNodeTexImage")
    image2.location.x = 0
    image2.location.y = 0

    self.image2 = random.choice(self.images)
    bpy.ops.image.new(name='ScreenSource2')
    source2 = bpy.data.images['ScreenSource2']
    source2.source = 'FILE'
    source2.filepath = self.image2
    image2.image = source2
    self.sources.append(source2)
    
    self.material.node_tree.links.new(
      material.inputs['Surface'], 
      self.fader.outputs[0]
    )
    self.material.node_tree.links.new(
      self.fader.inputs[1], 
      image1.outputs['Color']
    )
    self.material.node_tree.links.new(
      self.fader.inputs[2], 
      image2.outputs['Color']
    )
    self.object.data.materials.append(self.material)
    scene.collection.objects.link(self.object)

  
    
  def random(self,minsize = 0):
    global TWO_PI
    print("Skopescreen random")
    
    self.reset()
    
    if self.settings.rnd_rotz:
      self.rotation.z = rnd(
        self.settings.min_rotz,
        self.settings.max_rotz,
        self.settings.dist_rotz
      )
    
    if self.settings.rnd_scale:
      if minsize == 0:
        minsize = self.width * self.settings.min_scale
      minscale = minsize / self.width # assuming square
      scale = rnd(
        minscale,
        self.settings.max_scale,
        self.settings.dist_scale
      )
      self.scale.x = scale
      self.scale.y = scale

    if self.settings.rnd_img1:
      self.image1 = random.choice(self.images)

    if self.settings.rnd_img2:
      self.image2 = random.choice(self.images)

    if self.settings.rnd_fade:
      self.fade = rnd (
        self.settings.min_fade,
        self.settings.max_fade,
        self.settings.dist_fade
      )

  def mix(self, src, dst, pct = 0, easing='LINEAR'):
    print("SkopeScreen mix")
    self.rotation.z = mix(src.rotation.z,dst.rotation.z,pct,easing)
    self.scale.x = mix(src.scale.x,dst.scale.x,pct,easing)
    self.scale.y = mix(src.scale.y,dst.scale.y,pct,easing)
    self.fade = mix(src.fade,dst.fade,pct,easing)
    self.image1 = src.image1
    self.image2 = dst.image2

  def toJSON(self):
    return { 
      k:v for (k,v) in vars(self).items() 
      if not k in ['object','material','fader','sources'] 
    }
  
  def fromJSON(self,data):
    self.location.x = data["location"]["x"]
    self.location.y = data["location"]["y"]
    self.location.z = data["location"]["z"]
    self.rotation.x = data["rotation"]["x"]
    self.rotation.y = data["rotation"]["y"]
    self.rotation.z = data["rotation"]["z"]
    self.width = data['width']
    self.height = data['height']
    self.dist = data['dist']
    self.scale.x = data["scale"]["x"]
    self.scale.y = data["scale"]["y"]
    self.images = data["images"]
    self.image1 = data["image1"]
    self.image2 = data["image2"]
    self.fade = data["fade"]

  def apply(self,scene):
    if not self.object or not self.fader:
        raise Exception("SkopeScreen can not be applied")
    print("Skopescreen apply")
    self.object.rotation_euler.x = self.rotation.x
    self.object.rotation_euler.y = self.rotation.y
    self.object.rotation_euler.z = self.rotation.z
    self.object.location.x = self.location.x
    self.object.location.y = self.location.y
    self.object.location.z = self.location.z
    self.object.scale[0] = self.scale.x
    self.object.scale[2] = self.scale.y
    bpy.data.images['ScreenSource1'].filepath = self.image1
    bpy.data.images['ScreenSource2'].filepath = self.image2
    self.fader.inputs[0].default_value=self.fade
