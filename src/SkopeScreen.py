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
    "roughness" : {
      "fixed": 0
    },
    "image1": {
      "random": True
    },
    "image2": {
      "random": True
    },
    'sources': {
      'directory' : '',
      'globs': ['*.JPG','*.PNG']
    },
    'width': {
      'set' : 10.0
    },
    'height': {
      'set' : 10.0
    },
    'dist': {
      'set' : 0.0
    },
    'location_x': {
      'set' : 0
    },
    'location_y': {
      'set' : 0
    },
    'location_z': {
      'set' : 0
    },
    'rotation_x': {
      'set' : 0
    },
    'rotation_y': {
      'set' : 0
    },
    'scale': {
      'random': True,
      'default': 1,
      'minimum':.5,
      'maximum': 2,
      'distribution': 'LINEAR',
      # extend_radius: True
    },
    'fade': {
      'random': True,
      'default': .5,
      'minimum':0,
      'maximum': 1,
      'distribution': 'LINEAR',
    },
    'rotation_z': {
      'random': True,
      'default': 0,
      'minimum':0,
      'maximum': TWO_PI,
      'distribution': 'LINEAR',
    }

  })

  settingsOLD = dict2obj({

    "roughness.fixed": 0,

    "image1.random": True,
    "image2.random": True,

    "sources.directory": '',
    "sources.globs": ['*.JPG','*.PNG'],
    "width.set": 10.0,
    "height.set":10.0,
    "dist.set": 0.0,
    "def_location": {"x":0, "y":0, "z":0 },
    "def_rotation": {"x":0, "y":0, "z":0 },

    "scale.random" : True,
    "scale.default": {"x":1,"y":1},
    "scale.minimum" : .5,
    "scale.maximum": 2,
    "scale.distribution": "LINEAR",
    # "scale_extends_radius": True,

    "fade.random": True,
    "fade.default": .5,
    "fade.minimum": 0,
    "fade.maximum": 1,
    "fade.distribution": "LINEAR",

    "rotation_z.random": True,
    "rotation_z.default": 0,
    "rotation_z.minimum": 0,
    "rotation_z.maximum": TWO_PI,
    "rotation_z.distribution": "LINEAR"

  })

  def __init__(self,scene=None,inputdir=None):

    self.settings.sources.directory = inputdir
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

    self.width = self.settings.width.set
    self.height = self.settings.height.set
    self.location = {
      'x': self.settings.location_x.set,
      'y': self.settings.location_y.set,
      'z': self.settings.location_z.set
    }
    self.rotation = {
      'x': self.settings.rotation_x.set,
      'y': self.settings.rotation_y.set,
      'z': self.settings.rotation_z.default
    }
    self.scale = {
      'x': self.settings.scale.default,
      'y': self.settings.scale.default
    }
    self.fade = self.settings.fade.default
    self.dist = self.settings.dist.set
    self.images = []
    if self.settings.sources.directory:
      for pattern in self.settings.sources.globs:
        self.images.extend(glob.glob(self.settings.sources.directory+'/'+pattern.upper()))
        self.images.extend(glob.glob(self.settings.sources.directory+'/'+pattern.lower()))
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
    self.material.roughness = self.settings.roughness.fixed
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
    
    if self.settings.rotation_z.random:
      self.rotation['z'] = rnd(
        self.settings.rotation_z.minimum,
        self.settings.rotation_z.maximum,
        self.settings.rotation_z.distribution
      )
    
    if self.settings.scale.random:
      if minsize == 0:
        minsize = self.width * self.settings.scale.minimum
      minscale = minsize / self.width # assuming square
      scale = rnd(
        minscale,
        self.settings.scale.maximum,
        self.settings.scale.distribution
      )
      self.scale['x'] = scale
      self.scale['y'] = scale

    if self.settings.image1.random:
      self.image1 = random.choice(self.images)

    if self.settings.image2.random:
      self.image2 = random.choice(self.images)

    if self.settings.fade.random:
      self.fade = rnd (
        self.settings.fade.minimum,
        self.settings.fade.maximum,
        self.settings.fade.distribution
      )

  def mix(self, src, dst, pct = 0, easing='LINEAR'):
    print("SkopeScreen mix")
    self.rotation['z'] = mix(src.rotation['z'],dst.rotation['z'],pct,easing)
    self.scale['x'] = mix(src.scale['x'],dst.scale['x'],pct,easing)
    self.scale['y'] = mix(src.scale['y'],dst.scale['y'],pct,easing)
    self.fade = mix(src.fade,dst.fade,pct,easing)
    self.image1 = src.image1
    self.image2 = dst.image2

  def toJSON(self):
    return { 
      k:v for (k,v) in vars(self).items() 
      if not k in ['object','material','fader','sources'] 
    }
  
  def fromJSON(self,data):
    self.location['x'] = data["location"]["x"]
    self.location['y'] = data["location"]["y"]
    self.location['z'] = data["location"]["z"]
    self.rotation['x'] = data["rotation"]["x"]
    self.rotation['y'] = data["rotation"]["y"]
    self.rotation['z'] = data["rotation"]["z"]
    self.width = data['width']
    self.height = data['height']
    self.dist = data['dist']
    self.scale['x'] = data["scale"]["x"]
    self.scale['y'] = data["scale"]["y"]
    self.images = data["images"]
    self.image1 = data["image1"]
    self.image2 = data["image2"]
    self.fade = data["fade"]

  def apply(self,scene):
    if not self.object or not self.fader:
        raise Exception("SkopeScreen can not be applied")
    print("Skopescreen apply")
    self.object.rotation_euler.x = self.rotation['x']
    self.object.rotation_euler.y = self.rotation['y']
    self.object.rotation_euler.z = self.rotation['z']
    self.object.location.x = self.location['x']
    self.object.location.y = self.location['y']
    self.object.location.z = self.location['z']
    self.object.scale[0] = self.scale['x']
    self.object.scale[2] = self.scale['y']
    bpy.data.images['ScreenSource1'].filepath = self.image1
    bpy.data.images['ScreenSource2'].filepath = self.image2
    self.fader.inputs[0].default_value=self.fade
