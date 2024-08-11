import math
import random
import bpy
import bmesh
import math

from easings import mix
from SkopeSettings import SkopeSettings

PI=math.pi
TWO_PI=2*math.pi

class SkopeCone:

  settings = SkopeSettings({
    "roughness" : 0,
    "metallic" : 1,
    "diffuse_color" : (1,1,1,1),
    "height": 20,
    "radius": 4,
    "rotation": {
      "random": True,
      "default": 0,
      "minimum": 0,
      "maximum": TWO_PI,
      "distribution" : "UNIFORM",
      "delta": .1,
      "easing": "EASEINOUT"
    },
    # when creating a random skope,
    # set the amount of sides 
    "numsides": {
      "random": True,
      "default": 5,
      "minimum": 3,
      "maximum": 8,
      "distribution" : "UNIFORM",
      "delta": .1,
      # randomly make the number of sides on
      # the bottom less than on the top
      "warp": False
    } ,
    # randomly wiggle (offset) the vertices at the 
    # top and bottom of the skope, 1 = TWO_PI*radius/numsides
    "wiggle": {
      "random": True,
      "default": 0,
      "minimum": 0,
      "maximum": 1,
      "distribution" : "UNIFORM",
      "within_beams" : True,
      "rel_minimum": 0,
      "rel_maximum": 1/5,
      "delta": .1,
      "easing": "EASEINOUT",
      # if slant, wiggle vertices at the top
      # different than at the bottom  
      "slant": False
    },
    # if random>chance, create
    # a random bevel on all edges
    "bevel" : {
      "random": True,
      "default": False,
      "chance": .5,
      "fixed_limit_method": 'WEIGHT',
      "fixed_width": 4,
      "fixed_segments": 16,
      "fixed_harden_normals": True,
      "easing": "EASEINOUT"
    },
    # make bevels smooth
    # removed in blender4
    "smooth" : {
      "random": True,
      "default": True,
      "chance": .5
    },
    # use autosmooth, degrees
    # removed in blender4
    "autosmooth" : {
      "random": True,
      "default": 30,
      "minimum": 0,
      "maximum": 180,
      "distribution" : "UNIFORM",
      "delta": .1,
      "easing": "EASEINOUT"
    }
  })
  

  def __init__(self,scene=None):
    
    self.reset(0,None,False)
    if scene:
      cone = scene.objects.get("cone")
      if cone:
        raise Exception("Sorry, only one SkopeCone per scene")
      else:
        self.create(scene)
    else:
       self.mesh = None
       self.object = None
       self.bevel = None
       self.bmesh = None
       self.beams = []
       self.material = None

    if scene:
      self.apply(scene)
    
  def reset(self, numsides=0, smooth=None, rebuild=True):
    print("SkopeCone reset", numsides, smooth, rebuild)
    if numsides==0:
      self.numsides = self.settings.get('numsides')
    else:
      self.numsides = numsides
    if smooth is None:
      self.smooth = self.settings.get('smooth')
    else:
      self.smooth = smooth
    if self.smooth:
      self.autosmooth = self.settings.get('autosmooth')
    else:
      self.autosmooth = 0
    self.radius = self.settings.get('radius')
    self.height = self.settings.get('height')
    self.rotation = self.settings.get('rotation')
    self.enable_bevel = self.settings.bevel['random'] or self.settings.get('bevel')
    if rebuild:
      self.createBMesh()

  def create(self,scene):
    print("SkopeCone create")

    # create a object
    self.mesh = bpy.data.meshes.new("SkopeConeMesh")
    self.object = bpy.data.objects.new("cone",self.mesh)

    # insert bmesh into object
    self.createBMesh()
    self.bmesh.to_mesh(self.mesh)
    self.mesh.update()
    #self.bmesh.free()

    # set mirror shading
    self.material = bpy.data.materials.get('MirrorMaterial')

    if self.material is None:
        self.material = bpy.data.materials.new(name='MirrorMaterial')

    self.material.use_nodes = True

    if self.material.node_tree:
        self.material.node_tree.links.clear()
        self.material.node_tree.nodes.clear()

    self.material.roughness = self.settings.get('roughness')
    self.material.metallic = self.settings.get('metallic')
    self.material.diffuse_color=self.settings.get('diffuse_color')

    nodes = self.material.node_tree.nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')

    bdsf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bdsf.inputs[0].default_value = (1,1,1,1)
    bdsf.inputs[2].default_value[0] = 1
    bdsf.inputs[3].default_value = (1,1,1,1)
    bdsf.inputs[4].default_value = 0
    bdsf.inputs[7].default_value = 0
    bdsf.inputs[9].default_value = 0
    bdsf.inputs[6].default_value = 1
    bdsf.inputs[13].default_value = 0
    bdsf.inputs[15].default_value = 0
    bdsf.inputs[15].default_value = 0
    bdsf.inputs[16].default_value = 0
    bdsf.inputs[2].default_value[0] = 0
    bdsf.inputs[2].default_value[1] = 0
    bdsf.inputs[2].default_value[2] = 0

    # links the nodes in the material
    self.material.node_tree.links.new(bdsf.outputs[0], output.inputs[0])
    # link the material to the object
    self.object.data.materials.append(self.material)

    # add a bevel mod to the object
    if self.enable_bevel:
      self.bevel = self.object.modifiers.new(name="SkopeConeBevel", type='BEVEL')
      self.bevel.affect='EDGES'
      self.bevel.limit_method=self.settings.bevel['fixed_limit_method']
      self.bevel.width = self.settings.bevel['fixed_width']
      self.bevel.segments = self.settings.bevel['fixed_segments']
      self.bevel.harden_normals = self.settings.bevel['fixed_harden_normals']
    else:
      self.bevel = None

    # link the object to the scene
    scene.collection.objects.link(self.object)

  def createBMesh(self):

    self.bmesh = bmesh.new()
    step = float(360/self.numsides)
    angles = (x * step for x in range(0, self.numsides))
    self.beams = [];
    for alpha in angles:
       self.beams.append({
          'bottom': [
            self.radius*math.sin(math.radians(alpha)),
            self.radius*math.cos(math.radians(alpha)),
            0
          ],
          'top': [
            self.radius*math.sin(math.radians(alpha)),
            self.radius*math.cos(math.radians(alpha)),
            self.height
          ],
          'bevel': 0
       })
    for beam in self.beams:
       self.bmesh.verts.new(beam['bottom'])
       self.bmesh.verts.new(beam['top'])
        
    self.bmesh.verts.ensure_lookup_table()
    self.bmesh.faces.ensure_lookup_table()

    for index in range(0,len(self.beams)):
        face = self.bmesh.faces.new([
            self.bmesh.verts[index*2],
            self.bmesh.verts[index*2+1],
            self.bmesh.verts[(index*2+3)%len(self.bmesh.verts)],
            self.bmesh.verts[(index*2+2)%len(self.bmesh.verts)]
        ])
        face.smooth = self.smooth
  


  def random(self):
    global TWO_PI
    print("SkopeCone random")

    # smooth
    smooth = self.settings.rndbool('smooth')

    # numsides
    numsides = self.settings.rndint('numsides')
    
    # reset straight
    self.reset(numsides,smooth)
    
    if self.smooth:
      self.autosmooth = self.settings.rnd('autosmooth')

    # wiggle some
    if self.settings.wiggle['random']:
      if self.settings.wiggle['within_beams']:
        self.settings.wiggle['minimum'] = self.settings.wiggle['rel_minimum']*TWO_PI*self.radius/self.numsides
        self.settings.wiggle['maximum'] = self.settings.wiggle['rel_maximum']*TWO_PI*self.radius/self.numsides
      for index in range(0,len(self.beams)):
        random_angle = random.random()*360
        random_wiggle = self.settings.rnd('wiggle')
        self.beams[index]['bottom'][0] += random_wiggle*math.sin(random_angle)
        self.beams[index]['bottom'][1] += random_wiggle*math.cos(random_angle)
        if self.settings.wiggle['slant']:
          random_angle = random.random()*360
          random_wiggle = self.settings.rnd('wiggle')
          self.beams[index]['top'][0] += random_wiggle*math.sin(random_angle)
          self.beams[index]['top'][1] += random_wiggle*math.cos(random_angle)
        else:
          self.beams[index]['top'][0] = self.beams[index]['bottom'][0]
          self.beams[index]['top'][1] = self.beams[index]['bottom'][1]
    
    # set a random bevel on all beams
    if self.enable_bevel:
      for index in range(0,len(self.beams)):
        if self.settings.bevel['random']:
          if self.settings.rndbool('bevel'):
            self.beams[index]['bevel'] = random.random()
        elif self.settings.get('bevel'):
          self.beams[index]['bevel'] = random.random()

    # warp some. this will make the number of 
    # sides on the bottom less than those 
    # at the top
    if self.settings.numsides['warp']:
      warpnum = random.randint(self.settings.numsides['minimum'], self.numsides)
      newbeams = []
      for index in range(0,len(self.beams)):
        warpindex = math.floor(index*warpnum/self.numsides)
        print('warp',index,warpindex)
        newbeams.append({
          'top': self.beams[index]['top'],
          'bottom': [
            self.beams[warpindex]['bottom'][0],
            self.beams[warpindex]['bottom'][1],
            self.beams[warpindex]['bottom'][2],
          ],
          'bevel': self.beams[warpindex]['bevel']
        })
      self.beams = newbeams
        

    # rotate
    self.rotation = self.settings.rnd('rotation')

  def rnd_delta(self):
    print("SkopeScreen rnd_delta")
    self.radius = self.settings.rnd_delta('radius',self.radius)
    self.height = self.settings.rnd_delta('height',self.height)
    self.rotation = self.settings.rnd_delta('rotation',self.rotation)
    if self.smooth:
      self.autosmooth = self.settings.rnd_delta('autosmooth',self.autosmooth)
    if self.settings.wiggle['random']:
      self.removeWiggle()
      if self.settings.wiggle['within_beams']:
        self.settings.wiggle['minimum'] = self.settings.wiggle['rel_minimum']*TWO_PI*self.radius/self.numsides
        self.settings.wiggle['maximum'] = self.settings.wiggle['rel_maximum']*TWO_PI*self.radius/self.numsides
      for index in range(0,len(self.beams)):
        random_angle = random.random()*360
        random_wiggle = self.settings.rnd('wiggle')
        self.beams[index]['bottom'][0] += random_wiggle*math.sin(random_angle)
        self.beams[index]['bottom'][1] += random_wiggle*math.cos(random_angle)
        if self.settings.wiggle['slant']:
          random_angle = random.random()*360
          random_wiggle = self.settings.rnd('wiggle')
          self.beams[index]['top'][0] += random_wiggle*math.sin(random_angle)
          self.beams[index]['top'][1] += random_wiggle*math.cos(random_angle)
        else:
          self.beams[index]['top'][0] = self.beams[index]['bottom'][0]
          self.beams[index]['top'][1] = self.beams[index]['bottom'][1]

  def removeWiggle(self):
    step = float(360/self.numsides)
    angles = (x * step for x in range(0, self.numsides))
    for beam in self.beams:
      alpha = next(angles)
      print('removeWiggle',beam,alpha)
      beam['bottom'] = [
        self.radius*math.sin(math.radians(alpha)),
        self.radius*math.cos(math.radians(alpha)),
        0
      ]
      beam['top'] = [
        self.radius*math.sin(math.radians(alpha)),
        self.radius*math.cos(math.radians(alpha)),
        self.height
      ]

  def mix(self, src, dst, pct = 0):
    print("SkopeScreen mix")
    numsides = max(src.numsides,dst.numsides)
    smooth = dst.smooth
    if self.numsides != numsides or self.smooth != smooth:
      self.reset(numsides, smooth)
    self.autosmooth = mix(src.autosmooth,dst.autosmooth,pct)
    self.radius = mix(src.radius,dst.radius,pct)
    self.height = mix(src.height,dst.height,pct)
    self.rotation = mix(src.rotation,dst.rotation,pct,self.settings.rotation["easing"])
    srcnum = src.numsides
    dstnum = dst.numsides
    for index in range(0,len(self.beams)):
      srcindex = math.floor(index*srcnum/self.numsides)
      dstindex = math.floor(index*dstnum/self.numsides)
      print('from:',self.numsides,srcnum,dstnum)
      print('mix:',index,srcindex,dstindex)
      self.beams[index]['bottom'][0] = mix(
        src.beams[srcindex]['bottom'][0],
        dst.beams[dstindex]['bottom'][0],
        pct,self.settings.wiggle["easing"]
      )
      self.beams[index]['bottom'][1] = mix(
        src.beams[srcindex]['bottom'][1],
        dst.beams[dstindex]['bottom'][1],
        pct,self.settings.wiggle["easing"]
      )
      self.beams[index]['top'][0] = mix(
        src.beams[srcindex]['top'][0],
        dst.beams[dstindex]['top'][0],
        pct,self.settings.wiggle["easing"]
      )
      self.beams[index]['top'][1] = mix(
        src.beams[srcindex]['top'][1],
        dst.beams[dstindex]['top'][1],
        pct,self.settings.wiggle["easing"]
      )
      self.beams[index]['bevel'] = mix(
        src.beams[srcindex]['bevel'],
        dst.beams[dstindex]['bevel'],
        pct,self.settings.bevel["easing"]
      )
    

  def apply(self,scene):
    if not self.bmesh or not self.mesh or not self.object:
        raise Exception("SkopeCone can not be applied")
    print("SkopeCone apply")

    for index in range(0,len(self.beams)):
      self.bmesh.verts[index*2].co = self.beams[index]['bottom']
      self.bmesh.verts[index*2+1].co = self.beams[index]['top']
    self.bmesh.verts.ensure_lookup_table()

    if self.autosmooth:
      self.mesh.use_auto_smooth=True
      self.mesh.auto_smooth_angle=PI*self.autosmooth/180
    else:
      self.mesh.use_auto_smooth=False

    if self.enable_bevel:
      bevelWeightLayer = self.bmesh.edges.layers.bevel_weight.verify()
      self.bmesh.faces.ensure_lookup_table()
      for index in range(0,len(self.beams)):
          face = self.bmesh.faces[index]
          print("apply bevel",self.beams[index]['bevel'])
          for edge in face.edges:
            edge[bevelWeightLayer] = self.beams[index]['bevel']
    
    self.bmesh.to_mesh(self.mesh)
    self.mesh.update()
    self.object.rotation_euler.z = self.rotation
    


  def toJSON(self):
    return { 
      k:v for (k,v) in vars(self).items() 
      if not k in ['object','bevel','mesh','bmesh','material'] 
    }

  def fromJSON(self,data):
    self.rotation = data['rotation']
    self.numsides = data['numsides']
    self.radius = data['radius']
    self.height = data['height']
    self.smooth = data['smooth']
    self.autosmooth = data['autosmooth']
    self.createBMesh()
    self.beams = data['beams']
    
    