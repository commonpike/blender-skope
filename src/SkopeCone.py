import math
import random
import bpy
import bmesh
import math

PI=math.pi
TWO_PI=2*math.pi

class SkopeCone:

  minsides=3
  maxsides=16
  maxwiggle=1/5 # 1 = 100%
  smooth= True # removed in blender4
  autoSmooth=15 # removed in blender4
  allowSlant=True
  def __init__(self,scene=None):
    self.numsides=5
    self.radius=4
    self.height=10
    self.rotation=.5

    if scene:
      cone = scene.objects.get("cone")
      if cone:
        raise Exception("Sorry, only one SkopeCone per scene")
      else:
        self.create(scene)
    else:
       self.mesh = None
       self.object = None
       self.bmesh = None
       self.beams = []
       self.material = None
  
    

  def create(self,scene):
    print("SkopeCone create")

    # create a object
    self.mesh = bpy.data.meshes.new("SkopeConeMesh")
    self.object = bpy.data.objects.new("cone",self.mesh)
    
    self.mesh.use_auto_smooth=(SkopeCone.autoSmooth>0)
    self.mesh.auto_smooth_angle=PI*SkopeCone.autoSmooth/180

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
          ]
       })
    for beam in self.beams:
       self.bmesh.verts.new(beam['bottom'])
       self.bmesh.verts.new(beam['top'])
        
    self.bmesh.verts.ensure_lookup_table()

    for index in range(0,len(self.beams)):
        face = self.bmesh.faces.new([
            self.bmesh.verts[index*2],
            self.bmesh.verts[index*2+1],
            self.bmesh.verts[(index*2+3)%len(self.bmesh.verts)],
            self.bmesh.verts[(index*2+2)%len(self.bmesh.verts)]
        ])
        face.smooth = SkopeCone.smooth

  
  def reset(self, numsides=3):
    print("SkopeCone reset", numsides)
    self.numsides = numsides
    self.createBMesh()

  def random(self):
    global TWO_PI
    print("SkopeCone random")
    self.reset(
      random.randint(SkopeCone.minsides, SkopeCone.maxsides)
    )
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

    self.rotation = random.random()*360
    # radius
    # rotation

  def apply(self,scene):
    if not self.bmesh or not self.mesh or not self.object:
        raise Exception("SkopeCamera can not be applied")
    print("SkopeCone Apply")
    for index in range(0,len(self.beams)):
       self.bmesh.verts[index*2].co = self.beams[index]['bottom']
       self.bmesh.verts[index*2+1].co = self.beams[index]['top']
    self.bmesh.verts.ensure_lookup_table()
    self.bmesh.to_mesh(self.mesh)
    self.mesh.update()
    self.object.rotation_euler.z = self.rotation

  def toJSON(self):
    return { 
      k:v for (k,v) in vars(self).items() 
      if not k in ['object','mesh','bmesh','material'] 
    }

  def fromJSON(self,data):
    print("SkopeCone fromJSON")
    self.rotation = data['rotation']
    self.numsides = data['numsides']
    self.radius = data['radius']
    self.height = data['height']
    self.createBMesh()
    self.beams = data['beams']