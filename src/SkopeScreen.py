import bpy
import random
import glob
import math

from easings import mix
from SkopeSettings import SkopeSettings

PI=math.pi
TWO_PI=2*math.pi

class SkopeScreen:

  settings = SkopeSettings({
    'sources': {
      'directory' : '',
      'globs': ['*.JPG','*.PNG'],
      'random': True
    },
    "roughness" : 0,
    'width': 10.0,
    'height': 10.0,
    'dist':  0.0,
    'location_x':0,
    'location_y': 0,
    'location_z': 0,
    'rotation_x': 0,
    'rotation_y': 0,
    'scale': {
      'random': True,
      'default': 1,
      'minimum':.5,
      'maximum': 2,
      "distribution" : "UNIFORM",
      "extend_radius": True,
      'delta': .1,
      "easing": "EASEINOUT"
    },
    'rotation_z': {
      'random': True,
      'default': 0,
      'minimum':0,
      'maximum': TWO_PI,
      "distribution" : "UNIFORM",
      'delta': .1,
      "easing": "EASEINOUT"
    },
    "images_location": {
      "random": True,
      'default': 0,
      'minimum': -5,
      'maximum': 5,
      "distribution" : "UNIFORM",
      'delta': .1,
      "easing": "EASEINOUT"
    },
    "images_rotation": {
      "random": True,
      'default': 0,
      'minimum': 0,
      'maximum': TWO_PI,
      "distribution" : "UNIFORM",
      'delta': .05,
      "easing": "EASEINOUT"
    },
    "images_scale": {
      "random": True,
      'default': 1,
      'minimum': .5,
      'maximum': 1.5,
      "distribution" : "UNIFORM",
      'delta': .1,
      "easing": "EASEINOUT"
    },
    'images_fade': {
      'random': True,
      'default': .5,
      'minimum':0,
      'maximum': 1,
      "distribution" : "GAUSSIAN",
      'delta': .75,
      'fadeout_chance': .25,
      "easing": "EASEINOUT"
    }

  })

  def __init__(self,scene=None,inputdir=None):

    print("Skopescreen",inputdir)
    self.settings.sources['directory'] = inputdir
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
      self.mapping1 = None
      self.mapping2 = None
        
    if scene:
      self.apply(scene)


  def reset(self, reset_images=True):
    print("Skopescreen reset", reset_images)

    self.width = self.settings.get('width')
    self.height = self.settings.get('height')
    self.location = {
      'x': self.settings.get('location_x'),
      'y': self.settings.get('location_y'),
      'z': self.settings.get('location_z')
    }
    self.rotation = {
      'x': self.settings.get('rotation_x'),
      'y': self.settings.get('rotation_x'),
      'z': self.settings.get('rotation_z'),
    }
    self.scale = {
      'x': self.settings.get('scale'),
      'y': self.settings.get('scale'),
    }
    self.dist = self.settings.get('dist')
    if reset_images:
      print("reloading images",self.settings.sources['directory'])
      self.images = []
      if self.settings.sources['directory']:
        for pattern in self.settings.sources['globs']:
          self.images.extend(glob.glob(self.settings.sources['directory']+'/'+pattern.upper()))
          self.images.extend(glob.glob(self.settings.sources['directory']+'/'+pattern.lower()))
      
      self.image1 = {
          'src': '',
          'x': 0,
          'y': 0,
          'rotation': 0,
          'scale' : 1,
          'fade': .5
      }
      if len(self.images):
        self.image1['src'] =  self.images[0]
        
      self.image2 = {
          'src': '',
          'x': 0,
          'y': 0,
          'rotation': 0,
          'scale' : 1,
          'fade': .5
      }
      if len(self.images) > 1:
        self.image2['src'] =  self.images[1]

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
    self.material.name = "ScreenMaterial"
    self.material.roughness = self.settings.get('roughness')
    self.material.use_nodes = True
    self.material.node_tree.nodes.clear()
    
    output = self.material.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    output.name = 'Output'
    output.location.x = 600
    output.location.y = 200
    
    self.fader = self.material.node_tree.nodes.new(type="ShaderNodeMixShader")
    self.fader.name = 'Fader'
    self.fader.location.x = 400
    self.fader.location.y = 200
    
    self.sources = []

    imgnode1 = self.material.node_tree.nodes.new(type="ShaderNodeTexImage")
    imgnode1.name = "Image1"
    imgnode1.location.x = 0
    imgnode1.location.y = 400
    imgnode1.extension = 'MIRROR'

    self.image1['src'] = random.choice(self.images)
    bpy.ops.image.new(name='ScreenSource1')
    source1 = bpy.data.images['ScreenSource1']
    source1.source = 'FILE'
    source1.filepath = self.image1['src']
    imgnode1.image = source1
    self.sources.append(source1)

    coords1= self.material.node_tree.nodes.new(type="ShaderNodeTexCoord")
    coords1.name = "Coordinates1"
    coords1.location.x = -400
    coords1.location.y = 400

    self.mapping1= self.material.node_tree.nodes.new(type="ShaderNodeMapping")
    self.mapping1.name = "Mapping1"
    self.mapping1.location.x = -200
    self.mapping1.location.y = 400

    imgnode2 = self.material.node_tree.nodes.new(type="ShaderNodeTexImage")
    imgnode2.name = "Image2"
    imgnode2.location.x = 0
    imgnode2.location.y = 0
    imgnode2.extension = 'MIRROR'
    
    self.image2['src'] = random.choice(self.images)
    bpy.ops.image.new(name='ScreenSource2')
    source2 = bpy.data.images['ScreenSource2']
    source2.source = 'FILE'
    source2.filepath = self.image2['src']
    imgnode2.image = source2
    self.sources.append(source2)
    
    coords2= self.material.node_tree.nodes.new(type="ShaderNodeTexCoord")
    coords2.name = "Coordinates2"
    coords2.location.x = -400
    coords2.location.y = 0

    self.mapping2= self.material.node_tree.nodes.new(type="ShaderNodeMapping")
    self.mapping2.name  = "Mapping2"
    self.mapping2.location.x = -200
    self.mapping2.location.y = 0

    self.material.node_tree.links.new(
      output.inputs['Surface'], 
      self.fader.outputs[0]
    )
    self.material.node_tree.links.new(
      self.fader.inputs[1], 
      imgnode1.outputs['Color']
    )
    self.material.node_tree.links.new(
      imgnode1.inputs['Vector'],
      self.mapping1.outputs['Vector']
    )
    self.material.node_tree.links.new(
      self.mapping1.inputs['Vector'],
      coords1.outputs['Generated']
    )
    self.material.node_tree.links.new(
      self.fader.inputs[2], 
      imgnode2.outputs['Color']
    )
    self.material.node_tree.links.new(
      imgnode2.inputs['Vector'],
      self.mapping2.outputs['Vector']
    )
    self.material.node_tree.links.new(
      self.mapping2.inputs['Vector'],
      coords2.outputs['Generated']
    )
    self.object.data.materials.append(self.material)
    scene.collection.objects.link(self.object)

  
    
  def random(self,minsize = 0):
    global TWO_PI
    print("Skopescreen random")
    
    self.reset(False)
    
    self.rotation['z'] = self.settings.rnd('rotation_z')
    
    if self.settings.scale['random']:
      if self.settings.scale['extend_radius']:
        if minsize != 0:
          self.settings.scale['minimum'] = minsize / self.width
      scale = self.settings.rnd('scale')
      self.scale['x'] = scale
      self.scale['y'] = scale

    if len(self.images):
      if self.settings.sources['random']:
        self.image1['src'] = random.choice(self.images)
        self.image2['src'] = random.choice(self.images)

    self.image1['x'] = self.settings.rnd('images_location')
    self.image1['y'] = self.settings.rnd('images_location')
    self.image1['rotation'] = self.settings.rnd('images_rotation')
    self.image1['scale'] = self.settings.rnd('images_scale')
    self.image1['fade'] = self.settings.rnd('images_fade')

    self.image2['x'] = self.settings.rnd('images_location')
    self.image2['y'] = self.settings.rnd('images_location')
    self.image2['rotation'] = self.settings.rnd('images_rotation')
    self.image2['scale'] = self.settings.rnd('images_scale')
    self.image2['fade'] = self.settings.rnd('images_fade')

    

  def rnd_delta(self):
    print("SkopeScreen rnd_delta")

    fadeoutimg = ''
    if 2*random.random()*self.settings.images_fade['fadeout_chance'] < .5:
      fadeoutimg = random.choice(['image1','image2'])

    self.rotation['z'] = self.settings.rnd_delta('rotation_z',self.rotation['z'])
    scale = self.settings.rnd_delta('scale',self.scale['x'])
    self.scale['x'] = scale
    self.scale['y'] = scale

    self.image1['x'] = self.settings.rnd_delta('images_location',self.image1['x'])
    self.image1['y'] = self.settings.rnd_delta('images_location',self.image1['y'])
    self.image1['rotation'] = self.settings.rnd_delta('images_rotation',self.image1['rotation'])
    self.image1['scale'] = self.settings.rnd_delta('images_scale',self.image1['scale'])
    if self.image1['fade'] != 0 and fadeoutimg == 'image1':
      self.image1['fade'] = 0
    else:
      self.image1['fade'] = self.settings.rnd_delta('images_fade',self.image1['fade'])

    self.image2['x'] = self.settings.rnd_delta('images_location',self.image2['x'])
    self.image2['y'] = self.settings.rnd_delta('images_location',self.image2['y'])
    self.image2['rotation'] = self.settings.rnd_delta('images_rotation',self.image2['rotation'])
    self.image2['scale'] = self.settings.rnd_delta('images_scale',self.image2['scale'])
    if self.image2['fade'] != 0 and fadeoutimg == 'image2':
      print("fadeout2",self.image2['src'])
      self.image2['fade'] = 0
    else:
      self.image2['fade'] = self.settings.rnd_delta('images_fade',self.image2['fade'])

  def mix(self, src, dst, pct = 0):
    print("SkopeScreen mix")
    self.rotation['z'] = mix(src.rotation['z'],dst.rotation['z'],pct,self.settings.rotation_z['easing'])
    self.scale['x'] = mix(src.scale['x'],dst.scale['x'],pct,self.settings.scale['easing'])
    self.scale['y'] = mix(src.scale['y'],dst.scale['y'],pct,self.settings.scale['easing'])
    self.image1['src'] = src.image1['src']
    self.image2['src'] = dst.image2['src']
    self.image1['x'] = mix(src.image1['x'],dst.image1['x'],pct,self.settings.images_location['easing'])
    self.image1['y'] = mix(src.image1['y'],dst.image1['y'],pct,self.settings.images_location['easing'])
    self.image1['rotation'] = mix(src.image1['rotation'],dst.image1['rotation'],pct,self.settings.images_rotation['easing'])
    self.image1['scale'] = mix(src.image1['scale'],dst.image1['scale'],pct,self.settings.images_scale['easing'])
    self.image1['fade'] = mix(src.image1['fade'],dst.image1['fade'],pct,self.settings.images_fade['easing'])
    self.image2['x'] = mix(src.image2['x'],dst.image2['x'],pct,self.settings.images_location['easing'])
    self.image2['y'] = mix(src.image2['y'],dst.image2['y'],pct,self.settings.images_location['easing'])
    self.image2['rotation'] = mix(src.image2['rotation'],dst.image2['rotation'],pct,self.settings.images_rotation['easing'])
    self.image2['scale'] = mix(src.image2['scale'],dst.image2['scale'],pct,self.settings.images_scale['easing'])
    self.image2['fade'] = mix(src.image2['fade'],dst.image2['fade'],pct,self.settings.images_fade['easing'])

  def toJSON(self):
    return { 
      k:v for (k,v) in vars(self).items() 
      if not k in ['object','material','fader','sources','mapping1','mapping2'] 
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

  def apply(self,scene):

    print("Skopescreen apply")

    object = bpy.data.objects["screen"]
    image1 = bpy.data.images['ScreenSource1']
    image2 = bpy.data.images['ScreenSource2']
    material = bpy.data.materials["ScreenMaterial"]
    fader = material.node_tree.nodes["Fader"]
    mapping1 = material.node_tree.nodes["Mapping1"]
    mapping2 = material.node_tree.nodes["Mapping2"]

    if not object or not fader or not image1 or not image2 or not mapping1 or not mapping2:
      raise Exception("SkopeScreen can not be applied")

    object.rotation_euler.x = self.rotation['x']
    object.rotation_euler.y = self.rotation['y']
    object.rotation_euler.z = self.rotation['z']
    object.location.x = self.location['x']
    object.location.y = self.location['y']
    object.location.z = self.location['z']
    object.scale[0] = self.scale['x']
    object.scale[1] = self.scale['y']

    image1.filepath = self.image1['src']
    image2.filepath = self.image2['src']

    fader.inputs[0].default_value=self.getFade()

    mapping1.inputs[1].default_value[0] = self.image1['x']
    mapping1.inputs[1].default_value[1] = self.image1['y']
    mapping1.inputs[2].default_value[2] = self.image1['rotation']
    mapping1.inputs[3].default_value[0] = self.image1['scale']
    mapping1.inputs[3].default_value[1] = self.image1['scale']

    
    mapping2.inputs[1].default_value[0] = self.image2['x']
    mapping2.inputs[1].default_value[1] = self.image2['y']
    mapping2.inputs[2].default_value[2] = self.image2['rotation']
    mapping2.inputs[3].default_value[0] = self.image2['scale']
    mapping2.inputs[3].default_value[1] = self.image2['scale']

  # helpers -----

  def getFade(self):
    if self.image1['fade'] == 0:
      return 1
    if self.image2['fade'] == 0:
      return 0
    return self.image2['fade']/(self.image1['fade']+self.image2['fade'])
  
  def swapOneInvisibleImage(self):
    if len(self.images) and self.settings.sources['random']:
      if self.image1['fade'] == 0.0:
          print("fadein1",self.image1['src'])
          self.image1['src'] = random.choice(self.images)
      else:
        if self.image2['fade'] == 0.0:
            self.image2['src'] = random.choice(self.images)
            print("fadein2",self.image2['src'])
