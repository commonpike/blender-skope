import bpy
import random
import glob
import math

PI=math.pi
TWO_PI=2*math.pi

class SkopeScreen:

  src_globs=['*.JPG','*.PNG']

  def __init__(self,source_dir):

    self.images = []
    for pattern in self.src_globs:
      self.images.extend(glob.glob(source_dir+'/'+pattern.upper()))
      self.images.extend(glob.glob(source_dir+'/'+pattern.lower()))
    self.width = 30.0
    self.height = 30.0
    self.dist = 10.0

    scene = bpy.context.scene
    screen = scene.objects.get("screen")
    if screen:
      self.object = screen
    else:
      self.create(scene)
    
    self.maxscale=2
    self.rotation = {"x":0, "y":0, "z":0 }
    self.location = {"x":0, "y":0, "z":0 }
    self.scale = {"x":0, "y":0 }
    self.image1 = ""
    self.image2 = ""
    self.mix = .5
    self.readScene(scene)

  def create(self,scene):
    print("SkopeScreen create")

    vert = [
        (-self.width/2, self.dist, -self.height/2), 
        (self.width/2, self.dist, -self.height/2), 
        (-self.width/2, self.dist, self.height/2), 
        (self.width/2, self.dist, self.height/2)
    ]
    fac = [(0, 1, 3, 2)]
    screen_data = bpy.data.meshes.new("screen")
    screen_data.from_pydata(vert, [], fac)
    screen_data.uv_layers.new(name='ScreenUVMap')
    self.object = bpy.data.objects.new("screen", screen_data)

    screen_material = bpy.data.materials.new(name = "ScreenMaterial")
    screen_material.roughness = 0
    screen_material.use_nodes = True
    screen_material.node_tree.nodes.clear()
    
    material = screen_material.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    material.location.x = 600
    material.location.y = 200
    
    mix = screen_material.node_tree.nodes.new(type="ShaderNodeMixShader")
    mix.location.x = 400
    mix.location.y = 200
    
    image1 = screen_material.node_tree.nodes.new(type="ShaderNodeTexImage")
    image1.location.x = 0
    image1.location.y = 200

    bpy.ops.image.new(name='source1')
    source1 = bpy.data.images['source1']
    source1.filepath =random.choice(self.images)
    image1.image = source1

    image2 = screen_material.node_tree.nodes.new(type="ShaderNodeTexImage")
    image2.location.x = 0
    image2.location.y = 0

    bpy.ops.image.new(name='source2')
    source2 = bpy.data.images['source2']
    source2.filepath =random.choice(self.images)
    image2.image = source2
    
    screen_material.node_tree.links.new(
      material.inputs['Surface'], 
      mix.outputs[0]
    )
    screen_material.node_tree.links.new(
      mix.inputs[1], 
      image1.outputs['Color']
    )
    screen_material.node_tree.links.new(
      mix.inputs[2], 
      image2.outputs['Color']
    )
    self.object.data.materials.append(screen_material)
    scene.collection.objects.link(self.object)


  def readScene(self,scene):
    print("Skopescreen Read scene")
    
    # screen
    screen = scene.objects["screen"]
    self.location["x"] = screen.location.x
    self.location["y"] = screen.location.y
    self.location["z"] = screen.location.z
    self.rotation["x"] = screen.rotation_euler.x
    self.rotation["y"] = screen.rotation_euler.y
    self.rotation["z"] = screen.rotation_euler.z
    self.scale["x"] = screen.scale[0]
    self.scale["y"] = screen.scale[1]

  def reset(self):
    print("Skopescreen reset")
    self.rotation["y"] = 0
    self.scale["x"] = 1
    self.scale["y"] = 1
    self.image1 = random.choice(self.images)
    self.image2 = random.choice(self.images)
    self.mix = .5

  def random(self,minsize):
    global TWO_PI
    print("Skopescreen random")
    self.reset()
    self.rotation["y"] = TWO_PI*random.random()
    minscale = minsize / self.width # assuming square
    scale = minscale + random.random() * (self.maxscale - minscale)
    self.scale["x"] = scale
    self.scale["y"] = scale
    self.image1 = random.choice(self.images)
    self.image2 = random.choice(self.images)
    self.mix =random.random()

  def toJSON(self):
    return { k:v for (k,v) in vars(self).items() if not k == 'object' }
  
  def fromJSON(self,data):
    self.location["x"] = data["location"]["x"]
    self.location["y"] = data["location"]["y"]
    self.location["z"] = data["location"]["z"]
    self.rotation["x"] = data["rotation"]["x"]
    self.rotation["y"] = data["rotation"]["y"]
    self.scale["x"] = data["scale"]["x"]
    self.scale["y"] = data["scale"]["y"]
    self.rotation["z"] = data["rotation"]["z"]
    self.image1 = data["image1"]
    self.image2 = data["image2"]
    self.mix = data["mix"]

  def apply(self,scene):
    print("Skopescreen apply")
    
    # screen
    screen = scene.objects["screen"]
    screen.rotation_euler.x = self.rotation["x"]
    screen.rotation_euler.y = self.rotation["y"]
    screen.rotation_euler.z = self.rotation["z"]
    screen.location.x = self.location["x"]
    screen.location.y = self.location["y"]
    screen.location.z = self.location["z"]
    screen.scale[0] = self.scale["x"]
    screen.scale[2] = self.scale["y"]
    bpy.data.images['source1'].filepath = self.image1
    bpy.data.images['source2'].filepath = self.image2
    bpy.data.materials['image'].node_tree.nodes["Mix Shader"].inputs[0].default_value=self.mix
