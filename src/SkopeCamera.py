import bpy


from easings import rnd,mix
from utilities import dict2obj

class SkopeCamera:

  settings = dict2obj({

    "fix_lens": 70,
    "fix_sensor_width": 70,
    "fix_type": "PERSP",
    "fix_clip_start": .1,
    "fix_clip_end": 100,
    "fix_rotation": {"x":0, "y":0, "z":0 },

    "location_within_radius": True,
    "def_location" : {"x":0, "y":0, "z":10 },
    "rnd_location" : {"x":True, "y":True, "z":False },
    "min_location" : {"x":-5, "y":-5, "z":-1 },
    "max_location" : {"x":5, "y":5, "z":1 },
    "dist_location" : {"x":"LINEAR", "y":"LINEAR", "z":"LINEAR" },

    "rnd_shift" : True,
    "def_shift_x": 0,
    "def_shift_y": 0,
    "min_shift" : -.25,
    "max_shift" : .25,
    "dist_shift" : "LINEAR"
  })

  dist = 10
  maxshift = .5
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
    self.location = self.settings.def_location
    self.shift_x = self.settings.def_shift_x
    self.shift_y = self.settings.def_shift_y

  def create(self,scene):
    print("SkopeCamera creating camera")
    camera_data = bpy.data.cameras.new(name='camera')
    self.object = bpy.data.objects.new('camera', camera_data)
    self.object.location.x = self.settings.def_location.x
    self.object.location.y = self.settings.def_location.y
    self.object.location.z = self.settings.def_location.z
    self.object.data.shift_x = self.settings.def_shift_x
    self.object.data.shift_y = self.settings.def_shift_y
    
    self.object.data.lens = self.settings.fix_lens
    self.object.data.sensor_width = self.settings.fix_sensor_width
    self.object.data.type = self.settings.fix_type
    self.object.data.clip_start = self.settings.fix_clip_start
    self.object.data.clip_end = self.settings.fix_clip_end
    self.object.rotation_euler[0] = self.settings.fix_rotation.x
    self.object.rotation_euler[1] = self.settings.fix_rotation.y
    self.object.rotation_euler[2] = self.settings.fix_rotation.z
    scene.collection.objects.link(self.object)
    scene.camera = self.object ## ??



  def random(self, radius = 10):
    print("SkopeCamera random")
    self.reset()
    if not self.settings.location_within_radius or radius == 0:
        maxlocx = self.settings.max_location.x
        maxlocy = self.settings.max_location.y
        minlocx = self.settings.min_location.x
        minlocy = self.settings.min_location.y
    else :
        maxlocx = radius/2
        minlocx = -radius/2
        maxlocy = radius/2
        minlocy = -radius/2
    if self.settings.rnd_location.x:
      self.location.x = rnd(
        minlocx,
        maxlocx,
        self.settings.dist_location.x
      )
    if self.settings.rnd_location.y:
      self.location.y = rnd(
        minlocy,
        maxlocy,
        self.settings.dist_location.y
      )
    if self.settings.rnd_location.z:
      self.location.z = rnd(
        self.settings.min_location.z,
        self.settings.max_location.z,
        self.settings.dist_location.z
      )

    if self.settings.rnd_shift:
      self.shift_x = rnd(
        self.settings.min_shift,
        self.settings.max_shift,
        self.settings.dist_shift
      )
      self.shift_y = rnd(
        self.settings.min_shift,
        self.settings.max_shift,
        self.settings.dist_shift
      )

  def mix(self, src, dst, pct = 0, easing='LINEAR'):
    print("SkopeCamera mix")
    self.location.x = mix(src.location.x,dst.location.x,pct,easing)
    self.location.y = mix(src.location.y,dst.location.y,pct,easing)
    self.shift_x  = mix(src.shift_x,dst.shift_x,pct,easing)
    self.shift_y  = mix(src.shift_y,dst.shift_y,pct,easing)

  def apply(self,scene):
    if not self.object:
        raise Exception("SkopeCamera can not be applied")
    print("SkopeCamera apply")
    self.object.location.x = self.location.x
    self.object.location.y = self.location.y
    self.object.location.z = self.location.z
    self.object.data.shift_x = self.shift_x
    self.object.data.shift_y = self.shift_y

  def toJSON(self):
    return { k:v for (k,v) in vars(self).items() if not k == 'object' }
  
  def fromJSON(self,data):
    self.location.x = data["location"]["x"]
    self.location.y = data["location"]["y"]
    self.location.z = data["location"]["z"]
    self.shift_x = data["shift_x"]
    self.shift_y = data["shift_y"]