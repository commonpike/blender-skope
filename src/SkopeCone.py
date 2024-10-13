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
    "fixed": {
      "roughness" : 0.0,
      "metallic" : 1.0,
      "diffuse_color" : (1,1,1,1), 
      "enable_bevel" : True,
      "bevel_affect" : 'EDGES',
      "bevel_offset_type" : 'OFFSET',
      "bevel_limit_method": 'WEIGHT', # 'NONE',
      "bevel_width": 4.0, # 1
      "bevel_segments": 16,
      # bevel_harden_normals True works but generates autosmooth errors 
      # and seems to create glitches in the first frame of a clip
      "bevel_harden_normals": False, 
    },
    "height": {
      "default": 20.0,
    },
    "radius": {
      "default": 4.0
    },
    "rotation": {
      "random": True,
      "default": 0.0,
      "minimum": 0.0,
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
      "change_chance": .25,
      # randomly make the number of sides on
      # the bottom less than on the top
      "warp": False,
      "warp_chance" : .25
    } ,
    # randomly wiggle (offset) the vertices at the 
    # top and bottom of the skope, 1 = TWO_PI*radius/numsides
    "wiggle": {
      "random": True,
      "default": 0.0,
      "minimum": 0.0, 
      "maximum": 1.0, # set by code if within_beams ..
      "distribution" : "UNIFORM",
      "within_beams" : True,
      "rel_minimum": 0.0,
      "rel_maximum": .2,
      "delta": .1,
      "easing": "EASEINOUT",
      # if slant, wiggle vertices at the top
      # different than at the bottom  
      "slant": True
    },
    # if random>chance, create
    # a random bevel on all edges
    "bevel" : {
      "random": True,
      "default": False,
      "chance": .5,
      "distribution" : "UNIFORM",
      #"minimum": 0,
      #"maximum": 1,
      #"distribution" : "UNIFORM",
      #"delta": .1,
      "easing": "EASEINOUT", #?
    },
    # if bevel, randomize bevel weight
    # of every beam
    "bevel_weight" : {
      "random": True,
      "default": 0.5,
      "minimum": 0.0,
      "maximum": 1.0,
      "distribution" : "UNIFORM",
      "delta": .1,
      "easing": "EASEINOUT",
    },
    # make bevels smooth
    # removed in blender4
    # not animated between clips
    "smooth" : {
      "random": True,
      "default": True,
      "chance": .5
    },
    # if smooth, use autosmooth, degrees
    # set random:False and default 0.0 to disable
    # removed in blender4
    "autosmooth" : {
      "random": True,
      "default": 30.0,
      "minimum": 0.0,
      "maximum": 60.0, # 180
      "distribution" : "GAUSSIAN",
      "delta": .1,
      "easing": "EASEINOUT"
    }
  })
  

  def __init__(self,scene=None):

    if scene:
        self.createObjects(scene)
        self.applyFixedSettings()
        self.reset()
        self.apply(scene)
    else:
       self.bmesh = None
       self.beams = []
       self.reset()


    
  def createObjects(self,scene):
    print("SkopeCone createObjects")

    cone = scene.objects.get("cone")
    if cone:
      raise Exception("Sorry, only one SkopeCone per scene")

    # create a object
    mesh = bpy.data.meshes.new("SkopeConeMesh")    
    object = bpy.data.objects.new("cone",mesh)

    # create a material
    material = bpy.data.materials.new(name='MirrorMaterial')
    material.name = "MirrorMaterial"
    material.use_nodes = True
    # clean it up
    if material.node_tree:
        material.node_tree.links.clear()
        material.node_tree.nodes.clear()

    output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

    bdsf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
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
    material.node_tree.links.new(bdsf.outputs[0], output.inputs[0])
    
    # link the material to the object
    object.data.materials.append(material)

    # link the object to the scene
    scene.collection.objects.link(object)

  def createBeams(self, numsides):
    step = float(360/numsides)
    angles = (x * step for x in range(0, numsides))
    beams = [];
    for alpha in angles:
       beams.append({
          'bottom': [
            self.radius*math.sin(math.radians(alpha)),
            self.radius*math.cos(math.radians(alpha)),
            0.0
          ],
          'top': [
            self.radius*math.sin(math.radians(alpha)),
            self.radius*math.cos(math.radians(alpha)),
            self.height
          ],
          'bevel': 0.0
       })
    return beams
  
  def createBMesh(self, beams, smooth):

    new_bmesh = bmesh.new()
    for beam in beams:
       new_bmesh.verts.new(beam['bottom'])
       new_bmesh.verts.new(beam['top'])
        
    new_bmesh.verts.ensure_lookup_table()
    new_bmesh.faces.ensure_lookup_table()

    for index in range(0,len(beams)):
        face = new_bmesh.faces.new([
            new_bmesh.verts[index*2],
            new_bmesh.verts[index*2+1],
            new_bmesh.verts[(index*2+3)%len(new_bmesh.verts)],
            new_bmesh.verts[(index*2+2)%len(new_bmesh.verts)]
        ])
        face.smooth = self.smooth
    return new_bmesh

  def applyFixedSettings(self):
    print("SkopeCone applyFixedSettings")

    # update material
    material = bpy.data.materials.get('MirrorMaterial')
    if not material:
      raise Exception("MirrorMaterial can not be applied")
    
    # not sure if these show up, perhaps you have to
    # get into the material.node_tree...ShaderNodeBsdfPrincipled
    material.roughness = self.settings.fixed['roughness']
    material.metallic = self.settings.fixed['metallic']
    material.diffuse_color=self.settings.fixed['diffuse_color']
    
    # add or remove a bevel mod to the object
    object = bpy.data.objects["cone"]
    if not object:
      raise Exception("Bevel can not be applied")
    if self.settings.fixed['enable_bevel']:
      bevel = object.modifiers.get("SkopeConeBevel")
      if not bevel:
        print("Adding bevel modifier")
        bevel = object.modifiers.new(name="SkopeConeBevel", type='BEVEL')
      bevel.affect=self.settings.fixed['bevel_affect']
      bevel.offset_type=self.settings.fixed['bevel_offset_type']
      bevel.limit_method=self.settings.fixed['bevel_limit_method']
      bevel.width = self.settings.fixed['bevel_width']
      bevel.segments = self.settings.fixed['bevel_segments']
      bevel.harden_normals = self.settings.fixed['bevel_harden_normals']
    else:
      bevel = object.modifiers.get("SkopeConeBevel")
      if bevel:
        print("Removing bevel modifier")
        object.modifiers.remove(bevel)


  def reset(self):
    print("SkopeCone reset")
    
    # smooth 
    self.smooth = self.settings.get('smooth')
    
    # numsides  
    self.numsides = self.settings.get('numsides')
    
    # radius, height rotation
    self.radius = self.settings.get('radius')
    self.height = self.settings.get('height')
    self.rotation = self.settings.get('rotation')
    
    # autosmooth
    if self.smooth:
      self.autosmooth = self.settings.get('autosmooth')
    else:
      self.autosmooth = 0.0
    
    # beams and mesh
    self.beams = self.createBeams(self.numsides)
    self.bmesh = self.createBMesh(self.beams,self.smooth)
  
  def random(self):
    global TWO_PI
    print("SkopeCone random")

    # smooth
    self.smooth = self.settings.rndbool('smooth')

    # numsides
    self.numsides = self.settings.rndint('numsides')
 
    # radius, height, rotation
    self.radius = self.settings.rnd('radius')
    self.height = self.settings.rnd('height')
    self.rotation = self.settings.rnd('rotation')

    # autosmooth
    if self.smooth:
      self.autosmooth = self.settings.rnd('autosmooth')

    # beams, bmesh
    self.beams = self.createBeams(self.numsides)
    self.bmesh = self.createBMesh(self.beams,self.smooth)

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
    
    # bevel
    # set a random bevel on all beams
    if self.settings.fixed['enable_bevel']:
      for index in range(0,len(self.beams)):
        self.beams[index]['bevel'] = self.settings.rnd('bevel_weight') 

    # warp some
    # this will make the number of 
    # sides on the bottom less than those 
    # at the top
    if self.settings.numsides['warp']:
      if random.random() < self.settings.numsides['warp_chance']:
        warpnum = random.randint(self.settings.numsides['minimum'], self.numsides)
        newbeams = []
        for index in range(0,len(self.beams)):
          warpindex = round(index*warpnum/self.numsides)
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

  def rnd_delta(self):
    global TWO_PI
    print("SkopeScreen rnd_delta")

    # smooth
    # you cant delta from smooth to not smooth

    # numsides
    changing_numsides = False
    if self.settings.numsides['random']:
      if random.random() < self.settings.numsides['change_chance']:
        numsides = self.settings.rndint('numsides')
        if numsides != self.numsides:
          changing_numsides = True
          newbeams = self.createBeams(numsides)
          for index in range(0,len(newbeams)):
            oldindex = min(index,len(self.beams)-1)
            newbeams[index] = {
              'top': self.beams[oldindex]['top'],
              'bottom': self.beams[oldindex]['bottom'],
              'bevel': self.beams[oldindex]['bevel']
            }
          self.numsides = numsides
          self.beams = newbeams
          self.bmesh = self.createBMesh(self.beams,self.smooth)

    # radius, height, rotation
    self.radius = self.settings.rnd_delta('radius',self.radius)
    self.height = self.settings.rnd_delta('height',self.height)
    self.rotation = self.settings.rnd_delta('rotation',self.rotation)
    
    # autosmooth
    if self.smooth:
      self.autosmooth = self.settings.rnd_delta('autosmooth',self.autosmooth)
    
    # wiggle
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

    # bevel
    if self.settings.fixed['enable_bevel']:
      for index in range(0,len(self.beams)):
        if changing_numsides:
          # remove bevel on all beams; some of the 
          # beams may disappear at the end of the delta
          self.beams[index]['bevel'] = 0.0
        #elif self.beams[index]['bevel']:
        #  if self.settings.rndbool('bevel'):
        #    # remove bevel on beam index
        #    self.beams[index]['bevel'] = 0.0
        #  else:
        #    # delta bevel on beam index
        #    self.beams[index]['bevel'] = self.settings.rnd_delta('bevel_weight',self.beams[index]['bevel']) 
        else:
          if self.settings.rndbool('bevel'):
            # add bevel on beam index
            self.beams[index]['bevel'] = self.settings.rnd_delta('bevel_weight',self.beams[index]['bevel'])
          #else:
          #  # leave bevel as it is

    # warp
    if self.settings.numsides['warp']:
      if random.random() < self.settings.numsides['warp_chance']:
        warpnum = random.randint(self.settings.numsides['minimum'], self.numsides)
        newbeams = []
        for index in range(0,len(self.beams)):
          warpindex = round(index*warpnum/self.numsides)
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
    print("SkopeCone mix")
    
    # smooth
    prev_smooth = self.smooth
    self.smooth = dst.smooth
    
    # numsides
    prev_numsides = self.numsides
    self.numsides = max(src.numsides,dst.numsides)
    
    # radius, height, rotation
    self.radius = mix(src.radius,dst.radius,pct)
    self.height = mix(src.height,dst.height,pct)
    self.rotation = mix(src.rotation,dst.rotation,pct,self.settings.rotation["easing"])
    
    # autosmooth
    self.autosmooth = mix(src.autosmooth,dst.autosmooth,pct)
    
    # beams, bmesh
    if self.numsides != prev_numsides:
      self.beams = self.createBeams(self.numsides)
    if self.numsides != prev_numsides or self.smooth != prev_smooth:
      self.bmesh = self.createBMesh(self.beams,self.smooth)

    srcnum = src.numsides
    dstnum = dst.numsides
    for index in range(0,len(self.beams)):
      srcindex = math.floor(index*srcnum/self.numsides)
      dstindex = math.floor(index*dstnum/self.numsides)
      if srcindex != dstindex:
        print('numsides:',srcnum,"->",dstnum)
        print('src:',srcindex,'->',index,'; dst:',dstindex,'->',index)
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

    # bevel
    for index in range(0,len(self.beams)):
      srcindex = math.floor(index*srcnum/self.numsides)
      dstindex = math.floor(index*dstnum/self.numsides)
      self.beams[index]['bevel'] = mix(
        src.beams[srcindex]['bevel'],
        dst.beams[dstindex]['bevel'],
        pct,self.settings.bevel_weight["easing"]
      )

    # warp
    # no need to mix warp

  def apply(self,scene):
    print("SkopeCone apply")
    object = bpy.data.objects["cone"]
    mesh = bpy.data.meshes["SkopeConeMesh"]

    if not self.bmesh or not mesh or not object:
        raise Exception("SkopeCone can not be applied")

    for index in range(0,len(self.beams)):
      self.bmesh.verts[index*2].co = self.beams[index]['bottom']
      self.bmesh.verts[index*2+1].co = self.beams[index]['top']
    self.bmesh.verts.ensure_lookup_table()

    if self.smooth and self.autosmooth:
      mesh.use_auto_smooth=True
      mesh.auto_smooth_angle=PI*self.autosmooth/180
    else:
      mesh.use_auto_smooth=False

    if self.settings.fixed['enable_bevel']:
      bevelWeightLayer = self.bmesh.edges.layers.bevel_weight.verify()
      self.bmesh.faces.ensure_lookup_table()
      for index in range(0,len(self.beams)):
          face = self.bmesh.faces[index]
          print("apply bevel",index,self.beams[index]['bevel'])
          for edge in face.edges:
            edge[bevelWeightLayer] = self.beams[index]['bevel']
    
    self.bmesh.to_mesh(mesh)
    mesh.update()
    object.rotation_euler.z = self.rotation
    

  def getSettings(self):
    return self.settings

  def setSettings(self,settings):
    self.settings = SkopeSettings(settings)
    self.applyFixedSettings()

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
    self.beams = data['beams']
    self.bmesh = self.createBMesh(self.beams,self.smooth)
    