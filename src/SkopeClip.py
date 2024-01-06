from SkopeState import SkopeState

class SkopeClip:
  
  def __init__(self,scene,length):
    self.state = scene.skope.state
    self.start = self.state.clone()
    self.end = self.state.clone()
    self.length = length
    self.current = 0
    self.easing = 'LINEAR'

  def random(self):
    self.start.random()
    self.end.random()
    
  def start(self):
    return self.go(0)
  
  def end(self):
    return self.go(self.length-1)

  def back(self):
    return self.go(self.current-1)

  def step(self):
    return self.go(self.current+1)
  
  def go(self,frame):
    if frame < self.length:
      if frame >= 0:
        self.current = frame
    return self.current < self.length and self.current > 0

  def apply(self):
    pct = self.current * 100 / ( self.length - 1) # think twice
    self.state.mix(self.start,self.end,pct,self.easing)
    self.state.apply()