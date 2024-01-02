import bpy
import json

from SkopeMirrors import SkopeMirrors 
from SkopeCamera import SkopeCamera 
from SkopeScreen import SkopeScreen 

class SkopeState:

  frame_num=0
  num_frames=360

  def __init__(self,source_dir):
    self.camera = SkopeCamera()
    self.screen = SkopeScreen(source_dir)
    self.mirrors = SkopeMirrors()
    SkopeState.frame_num = bpy.context.scene.frame_current
    self.readScene(bpy.context.scene)

  def readScene(self,scene):
    print("SkopeState Read scene")
    self.screen.readScene(scene)
    self.camera.readScene(scene)
    self.mirrors.readScene(scene)

  def reset(self,num_mirrors=3):
    self.screen.reset()
    self.camera.reset()
    self.mirrors.reset(num_mirrors,0)
    
  def random(self):
    self.screen.random(2 * self.mirrors.inner_radius)
    self.camera.random(self.mirrors.inner_radius)
    self.mirrors.random()

  def apply(self,scene):
    print("Skopestate apply")
    self.screen.apply(scene)
    self.camera.apply(scene)
    self.mirrors.apply(scene)
    

  def writeJSON(self,file):
    print("Write json", file)
    with open(file, "w") as outfile:
      outfile.write(json.dumps(self,default=vars,indent=4))
    
  def readJSON(self,file):
    print("Read json", file)
    with open(file, "r") as infile:
      data = json.load(infile)
      self.fromJSON(data)

  def toJSON(self):
    return json.dumps(self,default=vars,indent=4)

  def fromJSON(self,data):
    self.screen.fromJSON(data['screen'])
    self.camera.fromJSON(data['camera'])
    self.mirrors.fromJSON(data['mirrors'])
    
