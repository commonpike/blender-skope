class KaleidoScopeScreen:
  def __init__(self):
    self.rotation = {"x":0, "y":0, "z":0 }
    self.location = {"x":0, "y":0, "z":0 }
    self.scale = {"x":0, "y":0 }
    self.image1 = ""
    self.image2 = ""
    self.mix = .5