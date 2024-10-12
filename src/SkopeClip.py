import math
import json

from SkopeState import SkopeState
from JSONEncoder import JSONEncoder 


class SkopeClip:
  
  def __init__(self,scene,length):
    self.id = 'init'
    self.state = scene.skope.state
    self.src = self.state.clone()
    self.dst = self.state.clone()
    self.length = length
    self.current = 0

  def reset(self,applyFixedSettings=False):
    self.src.reset(applyFixedSettings)
    self.dst = self.src.clone()
    self.id = self.src.id+'-'+self.dst.id

  def random(self):
    self.src.random()
    self.dst = self.src.clone()
    self.dst.rnd_delta()
    self.id = self.src.id+'-'+self.dst.id

  def reverse(self):
    old_dst = self.dst
    self.dst = self.src.clone()
    self.src = old_dst.clone()
    self.id = self.src.id+'-'+self.dst.id

  def start(self):
    return self.go(0)
  
  def end(self):
    return self.go(self.length-1)

  def back(self):
    return self.go(self.current-1)

  def step(self):
    return self.go(self.current+1)
  
  def go(self,frame):
    print("SkopeClip go "+str(frame))
    if frame < self.length:
      if frame >= 0:
        self.current = frame
        return True
    return False

  def next_delta(self):
    print("SkopeClip next_delta")
    self.dst.screen.swapOneInvisibleImage()
    self.src = self.dst.clone()
    self.dst.rnd_delta()
    self.id = self.src.id+'-'+self.dst.id

  def apply(self,scene):
    pct = self.current * 100.0 / ( self.length - 1) # think twice
    print("SkopeClip apply",pct)
    self.state.mix(self.src,self.dst,pct)
    self.state.apply(scene)

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
    return { 
      k:v for (k,v) in vars(self).items() 
      if not k in ['state','current'] 
    }

  
  def fromJSON(self,data):
    self.id = data['id']
    self.src.fromJSON(data['src'])
    self.dst.fromJSON(data['dst'])
