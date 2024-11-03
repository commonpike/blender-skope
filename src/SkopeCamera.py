import bpy

import math
from easings import mix
from SkopeSettings import SkopeSettings

PI=math.pi
TWO_PI=2*math.pi

class SkopeCamera:

  settings = SkopeSettings({
    "fixed": {
      "type": "PERSP",
      "clip_start": .1,
      "clip_end": 100.0
    },
    "rotation_x": {
      "default": 0.0,
      "random": True,
      "minimum": -TWO_PI/24,
      "maximum": TWO_PI/24,
      "distribution" : "UNIFORM",
      "delta": TWO_PI/72,
      "easing": "EASEINOUT"
    },
    "rotation_y": {
      "default": 0.0,
      "random": True,
      "minimum": -TWO_PI/24,
      "maximum": TWO_PI/24,
      "distribution" : "UNIFORM",
      "delta": TWO_PI/72,
      "easing": "EASEINOUT"
    },
    "rotation_z": {
      "default": 0.0,
      "random": True,
      "minimum": -TWO_PI/24,
      "maximum": TWO_PI/24,
      "distribution" : "UNIFORM",
      "delta": TWO_PI/72,
      "easing": "EASEINOUT"
    },
    "location_x": {
      "default": 0.0,
      "random": True,
      "minimum": -5.0,
      "maximum": 5.0,
      "distribution" : "UNIFORM",
      "within_radius": True,
      "delta": .5,
      "easing": "EASEINOUT"
    },
    "location_y": {
      "default": 0.0,
      "random": True,
      "minimum": -5.0,
      "maximum": 5.0,
      "distribution" : "UNIFORM",
      "within_radius": True,
      "delta": .5,
      "easing": "EASEINOUT"
    },
    "location_z": {
      "default": 10.0,
      "random": True,
      "minimum": 2.0,
      "maximum": 20.0,
      "distribution" : "UNIFORM",
      "delta": .5,
      "easing": "EASEINOUT"
    },
    "shift": {
      "random": True,
      "default": 0.0,
      "minimum": -.25,
      "maximum": .25,
      "distribution" : "UNIFORM",
      "delta": .5,
      "easing": "EASEINOUT"
    },
    "lens": {
      "random": True,
      "default": 70.0,
      "minimum": 10.0,
      "maximum": 100.0,
      "distribution" : "UNIFORM",
      "delta": .5,
      "easing": "EASEINOUT"
    },
    "sensor_width": {
      "random": True,
      "default": 70.0,
      "minimum": 10.0,
      "maximum": 100.0,
      "distribution" : "UNIFORM",
      "delta": .5,
      "easing": "EASEINOUT"
    },
  })

  def __init__(self,scene=None):
    if scene:
      self.createObject(scene)
      self.applyFixedSettings()
      self.reset()
      self.apply(scene)
    else:
      self.reset()

  def createObject(self,scene):
    print("SkopeCamera creating camera")
    camera = scene.objects.get("camera")
    if camera:
      raise Exception("Sorry, only one SkopeCamera per scene")
    camera_data = bpy.data.cameras.new(name='camera')
    object = bpy.data.objects.new('camera', camera_data)
    scene.collection.objects.link(object)
    scene.camera = object ## ??
    
  def applyFixedSettings(self):
    print("SkopeCamera applyFixedSettings")
    object = bpy.data.objects["camera"]
    if not object:
        raise Exception("SkopeCamera can not be found")
    object.data.type = self.settings.fixed['type']
    object.data.clip_start = self.settings.fixed['clip_start']
    object.data.clip_end = self.settings.fixed['clip_end']

  def reset(self):
    print("SkopeCamera Reset")
    self.rotation = {
      'x': self.settings.get('rotation_x'),
      'y': self.settings.get('rotation_y'),
      'z': self.settings.get('rotation_z')
    }
    self.location = {
      'x': self.settings.get('location_x'),
      'y': self.settings.get('location_y'),
      'z': self.settings.get('location_z')
    }
    self.shift_x = self.settings.get('shift')
    self.shift_y = self.settings.get('shift')
    self.lens = self.settings.get('lens')
    self.sensor_width = self.settings.get('sensor_width')

  def random(self, radius = 10):
    print("SkopeCamera random")
    self.reset()
    self.rotation['x'] = self.settings.rnd('rotation_x')  
    self.rotation['y'] = self.settings.rnd('rotation_y')  
    self.rotation['z'] = self.settings.rnd('rotation_y')
    if self.settings.location_x['within_radius']:
        self.settings.location_x['maximum'] = radius/2
        self.settings.location_x['minimum'] = -radius/2
    if self.settings.location_y['within_radius']:
        self.settings.location_y['maximum'] = radius/2
        self.settings.location_y['minimum'] = -radius/2
    self.location['x'] = self.settings.rnd('location_x')  
    self.location['y'] = self.settings.rnd('location_y')  
    self.location['z'] = self.settings.rnd('location_z')
    self.shift_x = self.settings.rnd('shift')
    self.shift_y = self.settings.rnd('shift')
    self.lens = self.settings.rnd('lens')
    self.sensor_width = self.settings.rnd('sensor_width')

  def rnd_delta(self):
    print("SkopeCamera rnd_delta")
    self.rotation['x'] = self.settings.rnd_delta('rotation_x',self.rotation['x'])  
    self.rotation['y'] = self.settings.rnd_delta('rotation_y',self.rotation['y']) 
    self.rotation['z'] = self.settings.rnd_delta('rotation_z',self.rotation['z']) 
    self.location['x'] = self.settings.rnd_delta('location_x',self.location['x'])  
    self.location['y'] = self.settings.rnd_delta('location_y',self.location['y']) 
    self.location['z'] = self.settings.rnd_delta('location_z',self.location['z']) 
    self.shift_x  = self.settings.rnd_delta('shift',self.shift_x)
    self.shift_y  = self.settings.rnd_delta('shift',self.shift_y)
    self.lens = self.settings.rnd_delta('lens',self.lens)
    self.sensor_width = self.settings.rnd_delta('sensor_width',self.sensor_width)

  def mix(self, src, dst, pct = 0):
    print("SkopeCamera mix")
    self.rotation['x'] = mix(src.rotation['x'],dst.rotation['x'],pct,self.settings.rotation_x['easing'])
    self.rotation['y'] = mix(src.rotation['y'],dst.rotation['y'],pct,self.settings.rotation_y['easing'])
    self.rotation['z'] = mix(src.rotation['z'],dst.rotation['z'],pct,self.settings.rotation_z['easing'])
    self.location['x'] = mix(src.location['x'],dst.location['x'],pct,self.settings.location_x['easing'])
    self.location['y'] = mix(src.location['y'],dst.location['y'],pct,self.settings.location_y['easing'])
    self.location['z'] = mix(src.location['z'],dst.location['z'],pct,self.settings.location_z['easing'])
    self.shift_x  = mix(src.shift_x,dst.shift_x,pct,self.settings.shift['easing'])
    self.shift_y  = mix(src.shift_y,dst.shift_y,pct,self.settings.shift['easing'])
    self.lens = mix(src.lens,dst.lens,pct,self.settings.lens['easing'])
    self.sensor_width = mix(src.sensor_width,dst.sensor_width,pct,self.settings.sensor_width['easing'])

  def apply(self,scene):
    print("SkopeCamera apply")
    object = bpy.data.objects["camera"]
    if not object:
        raise Exception("SkopeCamera can not be applied")
    object.rotation_euler[0] = self.rotation['x']
    object.rotation_euler[1] = self.rotation['y']
    object.rotation_euler[2] = self.rotation['z']
    object.location.x = self.location['x']
    object.location.y = self.location['y']
    object.location.z = self.location['z']
    object.data.shift_x = self.shift_x
    object.data.shift_y = self.shift_y
    object.data.lens = self.lens
    object.data.sensor_width = self.sensor_width

  def getSettings(self):
    return self.settings

  def setSettings(self,settings):
    self.settings = SkopeSettings(settings)
    self.applyFixedSettings()

  def toJSON(self):
    return { k:v for (k,v) in vars(self).items() if not k == 'object' }
  
  def fromJSON(self,data):
    self.rotation['x'] = data["rotation"]["x"]
    self.rotation['y'] = data["rotation"]["y"]
    self.rotation['z'] = data["rotation"]["z"]
    self.location['x'] = data["location"]["x"]
    self.location['y'] = data["location"]["y"]
    self.location['z'] = data["location"]["z"]
    self.shift_x = data["shift_x"]
    self.shift_y = data["shift_y"]
    self.lens = data["lens"]
    self.sensor_width = data["sensor_width"]