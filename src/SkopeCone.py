import math
import random
import bpy
import bmesh
import math

from easings import mix, rnd, rndint, rndbool
from utilities import dict2obj

PI=math.pi
TWO_PI=2*math.pi

class SkopeCone:

  settings = dict2obj({

    "fix_roughness": 0,
    "fix_metallic": 1,
    "fix_diffuse_color": (1,1,1,1),

    "set_height": 10,
    "set_radius": 4,

    "rnd_rotation": True,
    "def_rotation": 0,
    "min_rotation": 0,
    "max_rotation": 1,
    "dist_rotation": "LINEAR",

    # when creating a random skope,
    # set the amount of sides between these
    "rnd_numsides": True,
    "def_numsides": 5,
    "min_numsides": 3,
    "max_numsides" : 8,
    "dist_numsides" : "LINEAR",
    # sometimes make the number of sides on
    # the bottom less than on the top
    "warp_numsides": False, #allowWarp

    # randomly wiggle (offset) the vertices at the 
    # top and bottom of the skope, 1 = TWO_PI*radius/numsides
    "rnd_wiggle" : True,
    "min_wiggle" : 0,
    "max_wiggle": 1/5,
    "dist_wiggle": "LINEAR",
    # if allowSlant, wiggle vertices at the top
    # different than at the bottom
    "slant_wiggle": True, # allowSlant

    # if random>bevelChance, create
    # a random bevel on all edges
    "rnd_bevel" : True,
    "def_bevel": False,
    "chance_bevel": .5,
    "fix_bevel_limit_method": 'WEIGHT',
    "fix_bevel_width": 4,
    "fix_bevel_segments": 16,
    "fix_bevel_harden_normals": True,

    # make bevels smooth
    # removed in blender4
    "rnd_smooth" : True,
    "def_smooth": False,
    "chance_smooth": .5,

    # use autosmooth, degrees
    # removed in blender4
    "rnd_autosmooth": False,
    "def_autosmooth" : 0,
    "min_autosmooth" : 0,
    "max_autosmooth": 180,
    "dist_autosmooth": "LINEAR"

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
      self.numsides = self.settings.def_numsides
    else:
      self.numsides = numsides
    if smooth is None:
      self.smooth = self.settings.def_smooth
    else:
      self.smooth = smooth
    self.radius = self.settings.set_radius
    self.height = self.settings.set_height
    self.rotation = self.settings.def_rotation
    self.enable_bevel = self.settings.rnd_bevel or self.settings.def_bevel
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

    self.material.roughness = self.settings.fix_roughness
    self.material.metallic = self.settings.fix_metallic
    self.material.diffuse_color=self.settings.fix_diffuse_color

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
      self.bevel.limit_method=self.settings.fix_bevel_limit_method
      self.bevel.width = self.settings.fix_bevel_width
      self.bevel.segments = self.settings.fix_bevel_segments
      self.bevel.harden_normals = self.settings.fix_bevel_harden_normals
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
    if self.settings.rnd_smooth:
      smooth = rndbool(self.settings.chance_smooth)
    else:
      smooth = self.settings.def_smooth

    # numsides
    if self.settings.rnd_numsides:
      numsides = rndint(
        self.settings.min_numsides, 
        self.settings.max_numsides,
        self.settings.dist_numsides
      )
    else:
      numsides = self.settings.def_numsides

    # reset straight
    self.reset(numsides,smooth)
    
    # wiggle some
    if self.settings.rnd_wiggle:
      minwiggle = self.settings.min_wiggle*TWO_PI*self.radius/self.numsides
      maxwiggle = self.settings.max_wiggle*TWO_PI*self.radius/self.numsides
      for index in range(0,len(self.beams)):
        random_angle = rnd(0,360,'LINEAR')
        random_wiggle = rnd(minwiggle,maxwiggle,self.settings.dist_wiggle)
        self.beams[index]['bottom'][0] += random_wiggle*math.sin(random_angle)
        self.beams[index]['bottom'][1] += random_wiggle*math.cos(random_angle)
        if self.settings.slant_wiggle:
          random_angle = rnd(0,360,'LINEAR')
          random_wiggle = rnd(minwiggle,maxwiggle,self.settings.dist_wiggle)
          self.beams[index]['top'][0] += random_wiggle*math.sin(random_angle)
          self.beams[index]['top'][1] += random_wiggle*math.cos(random_angle)
        else:
          self.beams[index]['top'][0] = self.beams[index]['bottom'][0]
          self.beams[index]['top'][1] = self.beams[index]['bottom'][1]
    
    # set a random bevel on all beams
    if self.enable_bevel:
      for index in range(0,len(self.beams)):
        if self.settings.rnd_bevel:
          if rndbool(self.settings.chance_bevel):
            self.beams[index]['bevel'] = random.random()
        elif self.settings.def_bevel:
          self.beams[index]['bevel'] = random.random()

    # warp some. this will make the number of 
    # sides on the bottom less than those 
    # at the top
    if self.settings.warp_numsides:
      warpnum = random.randint(self.settings.min_numsides, self.numsides)
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
    if self.settings.rnd_rotation:
      self.rotation = rnd(
        self.settings.min_rotation,
        self.settings.max_rotation,
        self.settings.dist_rotation
      )*TWO_PI



  def mix(self, src, dst, pct = 0, easing='LINEAR'):
    print("SkopeScreen mix")
    numsides = max(src.numsides,dst.numsides)
    smooth = dst.smooth
    if self.numsides != numsides or self.smooth != smooth:
      self.reset(numsides)
    self.radius = mix(src.radius,dst.radius,pct,easing)
    self.height = mix(src.height,dst.height,pct,easing)
    self.rotation = mix(src.rotation,dst.rotation,pct,easing)
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
        pct,easing
      )
      self.beams[index]['bottom'][1] = mix(
        src.beams[srcindex]['bottom'][1],
        dst.beams[dstindex]['bottom'][1],
        pct,easing
      )
      self.beams[index]['top'][0] = mix(
        src.beams[srcindex]['top'][0],
        dst.beams[dstindex]['top'][0],
        pct,easing
      )
      self.beams[index]['top'][1] = mix(
        src.beams[srcindex]['top'][1],
        dst.beams[dstindex]['top'][1],
        pct,easing
      )
      self.beams[index]['bevel'] = mix(
        src.beams[srcindex]['bevel'],
        dst.beams[dstindex]['bevel'],
        pct,easing
      )
    

  def apply(self,scene):
    if not self.bmesh or not self.mesh or not self.object:
        raise Exception("SkopeCone can not be applied")
    print("SkopeCone apply")

    for index in range(0,len(self.beams)):
      self.bmesh.verts[index*2].co = self.beams[index]['bottom']
      self.bmesh.verts[index*2+1].co = self.beams[index]['top']
    self.bmesh.verts.ensure_lookup_table()

    if self.smooth:
      if self.settings.rnd_autosmooth:
        autosmooth = rnd(
          self.settings.min_autosmooth,
          self.settings.max_autosmooth,
          self.settings.dist_autosmooth
        )
      else:
        autosmooth = self.settings.def_autosmooth
      if autosmooth>0:
        self.mesh.use_auto_smooth=True
        self.mesh.auto_smooth_angle=PI*autosmooth/180
      else:
        self.mesh.use_auto_smooth=False
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
    self.createBMesh()
    self.beams = data['beams']
    
    