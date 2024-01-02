import random
import json

class SkopeCamera:
  def __init__(self):
    self.location = {"x":0, "y":0, "z":0 }
    #self.rotation: {"x":0, "y":0, "z":0 }

  def readScene(self,scene):
    print("SkopeCamera Read state")

    camera = scene.objects["camera"]
    self.location["x"] = camera.location.x
    self.location["y"] = camera.location.y
    self.location["z"] = camera.location.z

  def reset(self):
    print("SkopeCamera Reset")
    self.location["x"] = 0
    self.location["z"] = 0

  def random(self, maxloc):
    print("SkopeCamera random")
    self.reset()
    self.location["x"] = (random.random()-.5)*maxloc
    self.location["z"] = (random.random()-.5)*maxloc

  def apply(self,scene):
    print("SkopeCamera Apply state")

    camera = scene.objects["camera"]
    camera.location.x = self.location["x"]
    camera.location.y = self.location["y"]
    camera.location.z = self.location["z"]

  def toJSON(self):
    return json.dumps(self,default=vars,indent=4)

  def fromJSON(self,data):
    self.location["x"] = data["location"]["x"]
    self.location["y"] = data["location"]["y"]
    self.location["z"] = data["location"]["z"]