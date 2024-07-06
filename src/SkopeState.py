import bpy
import json

from JSONEncoder import JSONEncoder 
from SkopeCamera import SkopeCamera 
from SkopeScreen import SkopeScreen 
from SkopeCone import SkopeCone 

class SkopeState:

  frame_num=0
  num_frames=360

  def __init__(self,scene=None,inputdir=None):
    self.camera = SkopeCamera(scene)
    self.screen = SkopeScreen(scene,inputdir)
    self.cone = SkopeCone(scene)
    SkopeState.frame_num = bpy.context.scene.frame_current

  def reset(self,numsides=3):
    print("Skopestate reset")
    self.screen.reset()
    self.camera.reset()
    self.cone.reset(numsides)
    
  def random(self):
    print("Skopestate random")
    self.cone.random()
    self.screen.random(2 * self.cone.radius)
    self.camera.random(self.cone.radius)

  def rnd_delta(self):
    print("Skopestate rnd_delta")
    self.cone.rnd_delta()
    self.screen.rnd_delta()
    self.camera.rnd_delta()

  def apply(self,scene):
    print("Skopestate apply")
    self.screen.apply(scene)
    self.camera.apply(scene)
    self.cone.apply(scene)
    
  def clone(self):
    clone = SkopeState() # dont make a scene
    data = json.loads(json.dumps(self,cls=JSONEncoder))
    clone.fromJSON(data)
    return clone
  
  def mix(self,src,dst,pct,easing):
    self.screen.mix(src.screen,dst.screen,pct,easing)
    self.camera.mix(src.camera,dst.camera,pct,easing)
    self.cone.mix(src.cone,dst.cone,pct,easing)

  def writeJSON(self,file):
    print("Write json", file)
    with open(file, "w") as outfile:
      outfile.write(json.dumps(self,cls=JSONEncoder,indent=4))
    
  def readJSON(self,file):
    print("Read json", file)
    with open(file, "r") as infile:
      data = json.load(infile)
      self.fromJSON(data)

  def toJSON(self):
    return vars(self)
  
  def fromJSON(self,data):
    self.screen.fromJSON(data['screen'])
    self.camera.fromJSON(data['camera'])
    self.cone.fromJSON(data['cone'])
    
