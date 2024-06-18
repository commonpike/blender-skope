import bpy


from easings import rnd,mix
from utilities import dict2obj

class SkopeCamera:

  settings = dict2obj({
    "lens": {
      "fixed": 70
    },
    "sensor_width": {
      "fixed" : 70
    },
    "type": {
      "fixed" : "PERSP"
    },
    "clip_start": {
      "fixed" : .1
    },
    "clip_end": {
      "fixed" : 100
    },
    "rotation_x": {
      "fixed": 0
    },
    "rotation_y": {
      "fixed": 0
    },
    "rotation_z": {
      "fixed": 0
    },
    "location_x": {
      "default": 0,
      "random": True,
      "minimum": -5,
      "maximum": 5,
      "distribution": "LINEAR"
    },
    "location_y": {
      "default": 0,
      "random": True,
      "minimum": -5,
      "maximum": 5,
      "distribution": "LINEAR"
    },
    "location_z": {
      "default": 10,
      "random": False,
      "minimum": -1,
      "maximum": 1,
      "distribution": "LINEAR"
    },
    "location_within_radius": {
      "set": True
    },
    "shift": {
      "random": True,
      "default": 0,
      "minimum": -.25,
      "maximum": .25,
      "distribution": "LINEAR"
    }
  })

  def __init__(self,scene=None):
    if scene:
      camera = scene.objects.get("camera")
      if camera:
        raise Exception("Sorry, only one SkopeCamera per scene")
      else:
        self.create(scene)
    else:
        self.object = None
    self.reset()

    if scene:
      self.apply(scene)

  def reset(self):
    print("SkopeCamera Reset")
    self.location = {
      'x': self.settings.location_x.default,
      'y': self.settings.location_y.default,
      'z': self.settings.location_z.default
    }
    #self.location.x = self.settings.location_x.default
    #self.location.y = self.settings.location_y.default
    #self.location.z = self.settings.location_z.default
    self.shift_x = self.settings.shift.default
    self.shift_y = self.settings.shift.default

  def create(self,scene):
    print("SkopeCamera creating camera")
    camera_data = bpy.data.cameras.new(name='camera')
    self.object = bpy.data.objects.new('camera', camera_data)
    self.object.location.x = self.settings.location_x.default
    self.object.location.y = self.settings.location_y.default
    self.object.location.z = self.settings.location_z.default
    self.object.data.shift_x = self.settings.shift.default
    self.object.data.shift_y = self.settings.shift.default
    
    self.object.data.lens = self.settings.lens.fixed
    self.object.data.sensor_width = self.settings.sensor_width.fixed
    self.object.data.type = self.settings.type.fixed
    self.object.data.clip_start = self.settings.clip_start.fixed
    self.object.data.clip_end = self.settings.clip_end.fixed
    self.object.rotation_euler[0] = self.settings.rotation_x.fixed
    self.object.rotation_euler[1] = self.settings.rotation_y.fixed
    self.object.rotation_euler[2] = self.settings.rotation_z.fixed
    scene.collection.objects.link(self.object)
    scene.camera = self.object ## ??



  def random(self, radius = 10):
    print("SkopeCamera random")
    self.reset()
    if not self.settings.location_within_radius.set or radius == 0:
        maxlocx = self.settings.location_x.maximum
        maxlocy = self.settings.location_y.maximum
        minlocx = self.settings.location_x.minimum
        minlocy = self.settings.location_y.minimum
    else :
        maxlocx = radius/2
        minlocx = -radius/2
        maxlocy = radius/2
        minlocy = -radius/2
    if self.settings.location_x.random:
      self.location['x'] = rnd(
        minlocx,
        maxlocx,
        self.settings.location_x.distribution
      )
    if self.settings.location_y.random:
      self.location['y'] = rnd(
        minlocy,
        maxlocy,
        self.settings.location_y.distribution
      )
    if self.settings.location_z.random:
      self.location['z'] = rnd(
        self.settings.location_z.minimum,
        self.settings.location_z.maximum,
        self.settings.location_z.distribution
      )

    if self.settings.shift.random:
      self.shift_x = rnd(
        self.settings.shift.minimum,
        self.settings.shift.maximum,
        self.settings.shift.distribution
      )
      self.shift_y = rnd(
        self.settings.shift.minimum,
        self.settings.shift.maximum,
        self.settings.shift.distribution
      )

  def mix(self, src, dst, pct = 0, easing='LINEAR'):
    print("SkopeCamera mix")
    self.location['x'] = mix(src.location['x'],dst.location['x'],pct,easing)
    self.location['y'] = mix(src.location['y'],dst.location['y'],pct,easing)
    self.shift_x  = mix(src.shift_x,dst.shift_x,pct,easing)
    self.shift_y  = mix(src.shift_y,dst.shift_y,pct,easing)

  def apply(self,scene):
    if not self.object:
        raise Exception("SkopeCamera can not be applied")
    print("SkopeCamera apply")
    self.object.location.x = self.location['x']
    self.object.location.y = self.location['y']
    self.object.location.z = self.location['z']
    self.object.data.shift_x = self.shift_x
    self.object.data.shift_y = self.shift_y

  def toJSON(self):
    return { k:v for (k,v) in vars(self).items() if not k == 'object' }
  
  def fromJSON(self,data):
    self.location['x'] = data["location"]["x"]
    self.location['y'] = data["location"]["y"]
    self.location['z'] = data["location"]["z"]
    self.shift_x = data["shift_x"]
    self.shift_y = data["shift_y"]