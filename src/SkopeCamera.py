import bpy


from easings import mix
from SkopeSettings import SkopeSettings

class SkopeCamera:

  settings = SkopeSettings({
    "lens": 70,
    "sensor_width": 70,
    "type": "PERSP",
    "clip_start": .1,
    "clip_end": 100,
    "rotation_x": 0,
    "rotation_y": 0,
    "rotation_z": 0,
    "location_x": {
      "default": 0,
      "random": True,
      "minimum": -5,
      "maximum": 5,
      "distribution" : "UNIFORM",
      "within_radius": True,
      "delta": .5,
      "easing": "EASEINOUT"
    },
    "location_y": {
      "default": 0,
      "random": True,
      "minimum": -5,
      "maximum": 5,
      "distribution" : "UNIFORM",
      "within_radius": True,
      "delta": .5,
      "easing": "EASEINOUT"
    },
    "location_z": {
      "default": 10,
      "random": True,
      "minimum": 2,
      "maximum": 20,
      "distribution" : "UNIFORM",
      "delta": .5,
      "easing": "EASEINOUT"
    },
    "shift": {
      "random": True,
      "default": 0,
      "minimum": -.25,
      "maximum": .25,
      "distribution" : "UNIFORM",
      "delta": .5,
      "easing": "EASEINOUT"
    }
  })

  def __init__(self,scene=None):
    if scene:
      camera = scene.objects.get("camera")
      if camera:
        raise Exception("Sorry, only one SkopeCamera per scene")
      else:
        self.create(scene)
    self.reset()

    if scene:
      self.apply(scene)

  def reset(self):
    print("SkopeCamera Reset")
    self.location = {
      'x': self.settings.get('location_x'),
      'y': self.settings.get('location_y'),
      'z': self.settings.get('location_z')
    }
    self.shift_x = self.settings.get('shift')
    self.shift_y = self.settings.get('shift')

  def create(self,scene):
    print("SkopeCamera creating camera")
    camera_data = bpy.data.cameras.new(name='camera')
    object = bpy.data.objects.new('camera', camera_data)
    object.location.x = self.settings.get('location_x')
    object.location.y = self.settings.get('location_y')
    object.location.z = self.settings.get('location_z')
    object.data.shift_x = self.settings.get('shift')
    object.data.shift_y = self.settings.get('shift')
    
    object.data.lens = self.settings.get('lens')
    object.data.sensor_width = self.settings.get('sensor_width')
    object.data.type = self.settings.get('type')
    object.data.clip_start = self.settings.get('clip_start')
    object.data.clip_end = self.settings.get('clip_end')
    object.rotation_euler[0] = self.settings.get('rotation_x')
    object.rotation_euler[1] = self.settings.get('rotation_y')
    object.rotation_euler[2] = self.settings.get('rotation_z')
    scene.collection.objects.link(object)
    scene.camera = object ## ??



  def random(self, radius = 10):
    print("SkopeCamera random")
    self.reset()
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
    
  def rnd_delta(self):
    print("SkopeCamera rnd_delta")
    self.location['x'] = self.settings.rnd_delta('location_x',self.location['x'])  
    self.location['y'] = self.settings.rnd_delta('location_y',self.location['y']) 
    self.location['z'] = self.settings.rnd_delta('location_z',self.location['z']) 
    self.shift_x  = self.settings.rnd_delta('shift',self.shift_x)
    self.shift_y  = self.settings.rnd_delta('shift',self.shift_y)
    

  def mix(self, src, dst, pct = 0):
    print("SkopeCamera mix")
    self.location['x'] = mix(src.location['x'],dst.location['x'],pct,self.settings.location_x['easing'])
    self.location['y'] = mix(src.location['y'],dst.location['y'],pct,self.settings.location_y['easing'])
    self.location['z'] = mix(src.location['z'],dst.location['z'],pct,self.settings.location_z['easing'])
    self.shift_x  = mix(src.shift_x,dst.shift_x,pct,self.settings.shift['easing'])
    self.shift_y  = mix(src.shift_y,dst.shift_y,pct,self.settings.shift['easing'])

  def apply(self,scene):
    print("SkopeCamera apply")
    object = bpy.data.objects["camera"]
    if not object:
        raise Exception("SkopeCamera can not be applied")
    
    object.location.x = self.location['x']
    object.location.y = self.location['y']
    object.location.z = self.location['z']
    object.data.shift_x = self.shift_x
    object.data.shift_y = self.shift_y

  def toJSON(self):
    return { k:v for (k,v) in vars(self).items() if not k == 'object' }
  
  def fromJSON(self,data):
    self.location['x'] = data["location"]["x"]
    self.location['y'] = data["location"]["y"]
    self.location['z'] = data["location"]["z"]
    self.shift_x = data["shift_x"]
    self.shift_y = data["shift_y"]