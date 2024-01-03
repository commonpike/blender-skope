import bpy
import random
import glob
import math
import json

PI=math.pi
TWO_PI=2*math.pi

class SkopeScreen:

  src_globs=['*.JPG','*.PNG']

  def __init__(self,source_dir):
    self.images = []
    for pattern in self.src_globs:
      self.images.extend(glob.glob(source_dir+'/'+pattern.upper()))
      self.images.extend(glob.glob(source_dir+'/'+pattern.lower()))
    self.screen_scale=60
    self.rotation = {"x":0, "y":0, "z":0 }
    self.location = {"x":0, "y":0, "z":0 }
    self.scale = {"x":0, "y":0 }
    self.image1 = ""
    self.image2 = ""
    self.mix = .5

  def readScene(self,scene):
    print("Skopescreen Read scene")
    
    # screen
    screen = scene.objects["screen1"]
    self.location["x"] = screen.location.x
    self.location["y"] = screen.location.y
    self.location["z"] = screen.location.z
    self.rotation["x"] = screen.rotation_euler.x
    self.rotation["y"] = screen.rotation_euler.y
    self.rotation["z"] = screen.rotation_euler.z
    self.scale["x"] = screen.scale[0]
    self.scale["y"] = screen.scale[1]

  def reset(self):
    print("Skopescreen reset")
    self.rotation["y"] = 0
    self.scale["x"] = self.screen_scale / 2
    self.scale["y"] = self.screen_scale / 2
    self.image1 = random.choice(self.images)
    self.image2 = random.choice(self.images)
    self.mix = .5

  def random(self,minscale):
    global TWO_PI
    print("Skopescreen random")
    self.reset()
    self.rotation["y"] = TWO_PI*random.random()
    scale = minscale + random.random() * self.screen_scale
    self.scale["x"] = scale
    self.scale["y"] = scale
    self.image1 = random.choice(self.images)
    self.image2 = random.choice(self.images)
    self.mix =random.random()

  def toJSON(self):
    return vars(self)
  
  def fromJSON(self,data):
    self.location["x"] = data["location"]["x"]
    self.location["y"] = data["location"]["y"]
    self.location["z"] = data["location"]["z"]
    self.rotation["x"] = data["rotation"]["x"]
    self.rotation["y"] = data["rotation"]["y"]
    self.scale["x"] = data["scale"]["x"]
    self.scale["y"] = data["scale"]["y"]
    self.rotation["z"] = data["rotation"]["z"]
    self.image1 = data["image1"]
    self.image2 = data["image2"]
    self.mix = data["mix"]

  def apply(self,scene):
    print("Skopescreen apply")
    
    # screen
    screen = scene.objects["screen1"]
    screen.rotation_euler.x = self.rotation["x"]
    screen.rotation_euler.y = self.rotation["y"]
    screen.rotation_euler.z = self.rotation["z"]
    screen.location.x = self.location["x"]
    screen.location.y = self.location["y"]
    screen.location.z = self.location["z"]
    screen.scale[0] = self.scale["x"]
    screen.scale[1] = self.scale["y"]
    bpy.data.images['source1'].filepath = self.image1
    bpy.data.images['source2'].filepath = self.image2
    bpy.data.materials['image'].node_tree.nodes["Mix Shader"].inputs[0].default_value=self.mix
