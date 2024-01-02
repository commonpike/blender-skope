from KaleidoScopeState import KaleidoScopeState

class KaleidoScopeClip:
  
  interpolation = 'BEZIER'
  
  def __init__(self,source_dir):
    self.start = KaleidoScopeState(source_dir)
    self.end = KaleidoScopeState(source_dir)
    
  def set(self, settings = {}):
    for attr in settings:
      if attr == 'interpolation' : KaleidoScopeClip.interpolation = settings[attr]

  def randomizeStart(self,scene):
    self.start.randomize()
    self.start.apply(scene)
    self.start.setKeyFrame(scene,scene.frame_start)

  def randomizeEnd(self,scene):
    self.end.randomize()
    self.end.apply(scene)
    self.end.setKeyFrame(scene,scene.frame_end)

  def randomize(self,scene):
    self.randomizeStart(scene)
    self.randomizeEnd(scene)

  def reset(self,scene):
    self.start.readScene(scene)
    self.start.setKeyFrame(scene,scene.frame_start)
    self.start.readScene(scene)
    self.start.setKeyFrame(scene,scene.frame_end)