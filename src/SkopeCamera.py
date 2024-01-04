import bpy
import random
import math

class SkopeCamera:

  dist = 10
  def __init__(self):
    scene = bpy.context.scene
    camera = scene.objects.get("camera")
    if camera:
      self.object = camera
    else:
      self.create(scene)
    self.location = {"x":0, "y":0, "z":0 }

  def create(self,scene):
    print("SkopeCamera creating camera")
    camera_data = bpy.data.cameras.new(name='camera')
    self.object = bpy.data.objects.new('camera', camera_data)
    self.object.location.x = 0
    self.object.location.y = 0
    self.object.location.z = SkopeCamera.dist
    self.object.data.lens = 20
    self.object.data.type = 'PERSP'
    self.object.data.shift_x = 0
    self.object.data.shift_y = 0
    self.object.data.clip_start = .1
    self.object.data.clip_end = 100
    self.object.rotation_euler[0] = 0
    self.object.rotation_euler[1] = 0
    self.object.rotation_euler[2] = 0
    scene.collection.objects.link(self.object)
    scene.camera = self.object

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

  def apply(self,scene):
    print("SkopeCamera Apply state")
    self.object.location.x = self.location["x"]
    self.object.location.y = self.location["y"]
    self.object.location.z = self.location["z"]

  def toJSON(self):
    return { k:v for (k,v) in vars(self).items() if not k == 'object' }
  
  def fromJSON(self,data):
    self.location["x"] = data["location"]["x"]
    self.location["y"] = data["location"]["y"]
    self.location["z"] = data["location"]["z"]