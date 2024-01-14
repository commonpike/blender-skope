import bpy
import random
import math

from easings import mix

class SkopeCamera:

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
    self.location = {"x":0, "y":0, "z":SkopeCamera.dist }
    self.shift_x = 0
    self.shift_y = 0

    if scene:
      self.apply(scene)

  def create(self,scene):
    print("SkopeCamera creating camera")
    camera_data = bpy.data.cameras.new(name='camera')
    self.object = bpy.data.objects.new('camera', camera_data)
    self.object.location.x = 0
    self.object.location.y = 0
    self.object.location.z = SkopeCamera.dist
    self.object.data.lens = 70
    self.object.data.sensor_width = 70
    self.object.data.type = 'PERSP'
    self.object.data.shift_x = 0
    self.object.data.shift_y = 0
    self.object.data.clip_start = .1
    self.object.data.clip_end = 100
    self.object.rotation_euler[0] = 0
    self.object.rotation_euler[1] = 0
    self.object.rotation_euler[2] = 0
    scene.collection.objects.link(self.object)
    scene.camera = self.object ## ??

  def reset(self):
    print("SkopeCamera Reset")
    self.location["x"] = 0
    self.location["y"] = 0
    self.location["z"] = SkopeCamera.dist

  def random(self, maxloc = 10):
    print("SkopeCamera random")
    self.reset()
    self.location["x"] = (random.random()-.5)*maxloc
    self.location["y"] = (random.random()-.5)*maxloc
    self.shift_x = (random.random()-.5)*SkopeCamera.maxshift
    self.shift_y = (random.random()-.5)*SkopeCamera.maxshift

  def mix(self, src, dst, pct = 0, easing='LINEAR'):
    print("SkopeCamera mix")
    self.location["x"] = mix(src.location["x"],dst.location["x"],pct,easing)
    self.location["y"] = mix(src.location["y"],dst.location["y"],pct,easing)
    self.shift_x  = mix(src.shift_x,dst.shift_x,pct,easing)
    self.shift_y  = mix(src.shift_y,dst.shift_y,pct,easing)

  def apply(self,scene):
    if not self.object:
        raise Exception("SkopeCamera can not be applied")
    print("SkopeCamera apply")
    self.object.location.x = self.location["x"]
    self.object.location.y = self.location["y"]
    self.object.location.z = self.location["z"]
    self.object.data.shift_x = self.shift_x
    self.object.data.shift_y = self.shift_y

  def toJSON(self):
    return { k:v for (k,v) in vars(self).items() if not k == 'object' }
  
  def fromJSON(self,data):
    self.location["x"] = data["location"]["x"]
    self.location["y"] = data["location"]["y"]
    self.location["z"] = data["location"]["z"]