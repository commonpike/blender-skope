import math
import random

PI=math.pi
TWO_PI=2*math.pi

class SkopeMirror:
  def __init__(self):
    self.location = {"x":0, "y":0, "z":0 }
    self.rotation = {"x":0, "y":0, "z":0 }
    self.hide = False

class SkopeMirrors:

  max_mirrors=8
  
  def __init__(self):
    self.num_mirrors=5
    self.inner_radius=4
    self.mirror_shift=.5
    self.mirror_wiggle=1/5 # 1 = 100%
    self.mirrors = []
    for n in range(SkopeMirrors.max_mirrors):
      self.mirrors.append(SkopeMirror())

  def set(self, settings = {}):
    for attr in settings:
      if attr == 'num_mirrors' : self.num_mirrors = settings[attr]
      if attr == 'inner_radius' : self.inner_radius = settings[attr]
      if attr == 'mirror_shift' : self.mirror_shift = settings[attr]
      if attr == 'mirror_wiggle' : self.mirror_wiggle = settings[attr]

  def readScene(self,scene):
    print("SkopeMirrors Read scene")

    for n in range(self.num_mirrors):
      mirror = scene.objects["mirror"+str(n+1)]
      self.mirrors[n].location["x"] = mirror.location.x
      self.mirrors[n].location["y"] = mirror.location.y
      self.mirrors[n].location["z"] = mirror.location.z
      self.mirrors[n].rotation["x"] = mirror.rotation_euler.x
      self.mirrors[n].rotation["y"] = mirror.rotation_euler.y
      self.mirrors[n].rotation["z"] = mirror.rotation_euler.z
      self.mirrors[n].hide = mirror.hide_viewport

  def default_mirror_angle(self,n):
    global TWO_PI
    return (n+self.mirror_shift)*TWO_PI/self.num_mirrors - PI

  def default_mirror_center(self,n):
    a = self.default_mirror_angle(n)
    x = self.inner_radius*math.sin(a)
    y = self.inner_radius*math.cos(a)
    return x,y
  
  def reset(self, num_mirrors=3, mirror_shift=0):
    print("SkopeMirrors reset", num_mirrors, mirror_shift)
    
    self.num_mirrors = num_mirrors
    self.mirror_shift= mirror_shift
    
    for n in range(self.num_mirrors):
        mirror = self.mirrors[n]
        a=self.default_mirror_angle(n)
        x,z=self.default_mirror_center(n)
        #print('show mirror ',mirror,a,x,z)
        mirror.rotation["y"]=a
        mirror.location["x"]=x
        mirror.location["y"]=0
        mirror.location["z"]=z
        mirror.hide=False
        
    for n in range(self.num_mirrors,len(self.mirrors)):
        print('hide mirror ',mirror)
        mirror = self.mirrors[n]
        mirror.hide=True

  def random(self):
    global TWO_PI
    
    print("SkopeMirrors random")

    self.reset(
      random.randint(3, len(self.mirrors)),random.random()
    )
    for n in range(self.num_mirrors):
        print('wiggle ',n)
        mirror = self.mirrors[n]
        mirror.rotation["y"] += random.random()*TWO_PI*self.mirror_wiggle

  def apply(self,scene):
    print("SkopeMirrors Apply")

    # mirrors
    for n in range(self.max_mirrors):
      mirror = scene.objects["mirror"+str(n+1)]
      #print(mirror,self.mirrors[n])
      mirror.location.x = self.mirrors[n].location["x"]
      mirror.location.y = self.mirrors[n].location["y"]
      mirror.location.z = self.mirrors[n].location["z"]
      mirror.rotation_euler.x = self.mirrors[n].rotation["x"]
      mirror.rotation_euler.y = self.mirrors[n].rotation["y"]
      mirror.rotation_euler.z = self.mirrors[n].rotation["z"]
      mirror.hide_viewport = self.mirrors[n].hide
      mirror.hide_render = self.mirrors[n].hide

  def toJSON(self):
    return vars(self)

  def fromJSON(self,data):
    # self
    self.num_mirrors = data["num_mirrors"]
    self.inner_radius = data["inner_radius"]
    self.mirror_shift = data["mirror_shift"]
    
    # mirrors
    for n in range(len(data["mirrors"])):
      self.mirrors[n].location["x"] = data["mirrors"][n]["location"]["x"]
      self.mirrors[n].location["y"] = data["mirrors"][n]["location"]["y"]
      self.mirrors[n].location["z"] = data["mirrors"][n]["location"]["z"]
      self.mirrors[n].rotation["x"] = data["mirrors"][n]["rotation"]["x"]
      self.mirrors[n].rotation["y"] = data["mirrors"][n]["rotation"]["y"]
      self.mirrors[n].rotation["z"] = data["mirrors"][n]["rotation"]["z"]
      self.mirrors[n].hide = data["mirrors"][n]["hide"]