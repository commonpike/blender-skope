from SkopeState import SkopeState
import math



class SkopeClip:
  
  def __init__(self,scene,length):
    self.state = scene.skope.state
    self.src = self.state.clone()
    self.dst = self.state.clone()
    self.length = length
    self.current = 0
    self.easing = 'LINEAR'

  def random(self):
    self.src.random()
    self.dst.random()
    
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
    done = self.current < self.length - 1 and self.current > 0
    return not done

  def apply(self,scene):
    pct = self.current * 100 / ( self.length - 1) # think twice
    print("SkopeClip apply",pct);
    self.state.mix(self.src,self.dst,pct,self.easing)
    self.state.apply(scene)

  