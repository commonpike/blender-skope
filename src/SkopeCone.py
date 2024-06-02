import math
import random
import bpy
import bmesh
import math

from easings import mix

PI=math.pi
TWO_PI=2*math.pi

class SkopeCone:

  # when creating a random skope,
  # set the amount of sides between these
  minsides=3
  maxsides=8
  
  # randomly wiggle (offset) the vertices at the 
  # top and bottom of the skope, 1 = 100%
  maxwiggle=1/5 
  
  # if allowSlant, wiggle vertices at the top
  # different than at the bottom
  allowSlant=True

  # sometimes make the number of sides on
  # the bottom less than on the top
  allowWarp=False
  
  # if random>bevelChance, create
  # a random bevel on all edges
  bevelChance = .5
  bevelLimitMethod = 'WEIGHT'
  bevelWidth = 4
  bevelSegments = 16
  bevelHardenNormals = True

  # make bevels smooth
  smoothChance=.5
  smooth=False # removed in blender4
  autoSmooth=0 # angle; removed in blender4

  

  def __init__(self,scene=None):
    self.numsides=5
    self.radius=4
    self.height=10
    self.rotation=0
    self.smooth=SkopeCone.smooth

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

    self.material.roughness = 0
    self.material.metallic = 1
    self.material.diffuse_color=(1,1,1,1)

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
    if SkopeCone.bevelChance:
      self.bevel = self.object.modifiers.new(name="SkopeConeBevel", type='BEVEL')
      self.bevel.affect='EDGES'
      self.bevel.limit_method=SkopeCone.bevelLimitMethod
      self.bevel.width = SkopeCone.bevelWidth
      self.bevel.segments = SkopeCone.bevelSegments
      self.bevel.harden_normals = SkopeCone.bevelHardenNormals
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
  
  def reset(self, numsides=3):
    print("SkopeCone reset", numsides)
    self.numsides = numsides
    self.createBMesh()

  def random(self):
    global TWO_PI
    print("SkopeCone random")

    # smooth
    self.smooth = (random.random() < SkopeCone.smoothChance)

    # reset straight
    self.reset(
      random.randint(SkopeCone.minsides, SkopeCone.maxsides)
    )
    
    # wiggle some
    maxwiggle = SkopeCone.maxwiggle*TWO_PI*self.radius/self.numsides
    for index in range(0,len(self.beams)):
      random_angle = random.random()*360
      random_wiggle = random.random()*maxwiggle
      self.beams[index]['bottom'][0] += random_wiggle*math.sin(random_angle)
      self.beams[index]['bottom'][1] += random_wiggle*math.cos(random_angle)
      random_angle = random.random()*360
      if SkopeCone.allowSlant:
        random_wiggle = random.random()*maxwiggle
        self.beams[index]['top'][0] += random_wiggle*math.sin(random_angle)
        self.beams[index]['top'][1] += random_wiggle*math.cos(random_angle)
      else:
        self.beams[index]['top'][0] = self.beams[index]['bottom'][0]
        self.beams[index]['top'][1] = self.beams[index]['bottom'][1]
    
    # set a random bevel on all beams
    if SkopeCone.bevelChance:
      for index in range(0,len(self.beams)):
        if random.random() < SkopeCone.bevelChance:
          self.beams[index]['bevel'] = random.random()

    # warp some. this will make the number of 
    # sides on the bottom less than those 
    # at the top
    if SkopeCone.allowWarp:
      warpnum = random.randint(SkopeCone.minsides, self.numsides)
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
    self.rotation = random.random()*TWO_PI

    # radius
    # ...


  def mix(self, src, dst, pct = 0, easing='LINEAR'):
    print("SkopeScreen mix")
    self.rotation = mix(src.rotation,dst.rotation,pct,easing)
    numsides = max(src.numsides,dst.numsides)
    if (self.numsides != numsides):
      self.reset(numsides)
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

    if self.smooth and SkopeCone.autoSmooth>0:
      self.mesh.use_auto_smooth=True
      self.mesh.auto_smooth_angle=PI*SkopeCone.autoSmooth/180
    else:
      self.mesh.use_auto_smooth=False

    if SkopeCone.bevelChance:
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
    
    