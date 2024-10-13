import bpy
import json
import uuid

from JSONEncoder import JSONEncoder 
from SkopeCamera import SkopeCamera 
from SkopeScreen import SkopeScreen 
from SkopeCone import SkopeCone 

class SkopeState:

  #frame_num=0
  # num_frames=360

  def __init__(self,scene=None,inputdir=None):
    self.id = 'init';
    self.delta = 0
    self.camera = SkopeCamera(scene)
    self.screen = SkopeScreen(scene,inputdir)
    self.cone = SkopeCone(scene)
    #SkopeState.frame_num = bpy.context.scene.frame_current

  def reset(self,applyFixedSettings=False):
    print("Skopestate reset")
    if applyFixedSettings:
      self.screen.applyFixedSettings()
      self.camera.applyFixedSettings()
      self.cone.applyFixedSettings()
    self.screen.reset()
    self.camera.reset()
    self.cone.reset()
    # broken since 
    # https://github.com/commonpike/blender-skope/commit/dd81c68bd427556ed55284ccd505801f8e20318f#diff-29d2025da89dff0e23e91af099479b7eb7d31a4c229b66e02bad44a1be4a93b5L133
    # cant apply after reset
    #self.cone.reset()
    self.id = f'rset{self.cone.settings.get("numsides")}';
    
  def random(self):
    print("Skopestate random")
    self.cone.random()
    self.screen.random(2 * self.cone.radius)
    self.camera.random(self.cone.radius)
    self.id = str(uuid.uuid4())[:4];

  def rnd_delta(self):
    print("Skopestate rnd_delta")
    self.cone.rnd_delta()
    self.screen.rnd_delta()
    self.camera.rnd_delta()
    self.id = str(uuid.uuid4())[:4];

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
  
  def mix(self,src,dst,pct):
    self.screen.mix(src.screen,dst.screen,pct)
    self.camera.mix(src.camera,dst.camera,pct)
    self.cone.mix(src.cone,dst.cone,pct)
    self.id = src.id + '-' + dst.id + '-' + str(round(pct))

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
    self.id = data['id']
    self.screen.fromJSON(data['screen'])
    self.camera.fromJSON(data['camera'])
    self.cone.fromJSON(data['cone'])
    
