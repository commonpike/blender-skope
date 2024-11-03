import bpy
import math
import glob
import os
import re
import random
import json

from SkopeSettings import SkopeSettings
from SkopeState import SkopeState
from SkopeClip import SkopeClip
from SkopePanelFactory import SkopePanelFactory

class Skope:
  """A kaleidoscope for use in blender"""
  
  settings = SkopeSettings({
    'fixed': {
      'output_dir': '',
      'import_dir': '',
      'length': 360,
      'amount': 10,
      'width': 1920,
      'height': 1920,
      'scale': 20,
      'image_format': 'PNG',
      'video_format': 'FFMPEG',
      'ffmpeg_format': 'MPEG4',
      'motion_blur': False,
      'motion_blur_shutter': 8,
      'motion_blur_shape': 'SHARP'
    },
    'loop': {
      'loop_branch_chance' : 0,
      'loop_reverse_chance': 0
    }
  })

  def __init__(self, project_dir):
  
    print("Kaleidoscope init",project_dir)
    
    self.type = 'none' #stills | clips | loops

    self.rendering = False
    self.frozen = False

    # tie yourself to the scene
    bpy.types.Scene.skope=self
    
    # create current state
    scene = bpy.context.scene
    self.state = SkopeState(scene)

    # create optional clip
    self.clip = None

    # set correct dirs 
    self.setProjectDir(project_dir)
  
  def reset(self,applyFixedSettings=False):
    print("Skope reset")
    scene = bpy.context.scene
    if applyFixedSettings:
      self.applyFixedSettings()
    if self.clip:
      self.clip.reset(applyFixedSettings)
    self.state.reset(applyFixedSettings)
    self.state.apply(scene)
  
  def applyFixedSettings(self):
    scene = bpy.context.scene
    scene.frame_end = self.settings.fixed['length'] # +-1 ?
    scene.frame_set(1)
    scene.render.resolution_x = self.settings.fixed['width']
    scene.render.resolution_y = self.settings.fixed['height']
    scene.render.resolution_percentage = self.settings.fixed['scale']
    filename = scene.skope.state.id
    if self.type == 'stills':
      scene.render.image_settings.file_format = self.settings.fixed['image_format']
    else:
      scene.render.image_settings.file_format = self.settings.fixed['video_format']
      scene.render.ffmpeg.format=self.settings.fixed['ffmpeg_format']
      filename += '-'
    scene.render.filepath = self.settings.fixed['output_dir']+ '/' + filename
    
    if self.settings.fixed['motion_blur']:
      scene.render.use_motion_blur = True  
      scene.cycles.motion_blur_position = 'START'  
      scene.render.motion_blur_shutter = self.settings.fixed['motion_blur_shutter']  
      bpy.ops.render.shutter_curve_preset(shape = self.settings.fixed['motion_blur_shape'])
    else:
      scene.render.use_motion_blur = False

    bpy.context.view_layer.objects.active = bpy.data.objects["screen"]

    
  def setProjectDir(self,project_dir,reset=False):
    print("setProjectDir "+project_dir)

    if not os.path.exists(project_dir) or not os.path.isdir(project_dir):
      raise Exception("--project-dir "+project_dir+" is not a directory")
    
    input_dir = project_dir+'/input'
    output_dir = project_dir+'/output'
    import_dir = project_dir+'/import'
  
    if not os.path.isdir(input_dir):
      # if project_dir contains images, create input_dir
      # and move all images to the input_dir
      images = []
      for pattern in ['*.jpg','*.jpeg','*.png']:
        images.extend(glob.glob(project_dir+'/'+pattern.upper()))
        images.extend(glob.glob(project_dir+'/'+pattern.lower()))
      if not len(images):
        raise Exception(input_dir+" does not exist and "+output_dir+" contains no images")
      print("Creating "+input_dir+" and moving images from "+output_dir+" there..")
      os.makedirs(input_dir)
      for image in images:
          newimage = input_dir+"/"+os.path.basename(image)
          os.rename(image, newimage)

    if not os.path.exists(output_dir):
      os.makedirs(output_dir)
    elif not os.path.isdir(output_dir):
      raise Exception("--output-dir "+output_dir+" is not a directory")
    if not os.path.exists(import_dir):
      os.makedirs(import_dir)
    elif not os.path.isdir(import_dir):
      raise Exception("--import-dir "+import_dir+" is not a directory")

    self.project_dir = project_dir
    self.settings.fixed['import_dir'] = import_dir
    self.settings.fixed['output_dir'] = output_dir
    self.state.screen.settings.sources['directory'] = input_dir
    if reset:
      self.reset(True)

  def loadSettings(self,path):
    print("Skope loadSettings", path)
    with open(path, "r") as infile:
      settings = json.load(infile)
      self.settings = SkopeSettings(settings['skope'])
      self.applyFixedSettings()
      self.state.setSettings(settings['state'])
        
  def saveSettings(self,path):
    print("Skope saveSettings", path)
    settings = {
      "skope": self.settings,
      "state": self.state.getSettings()
    }
    with open(path, "w") as outfile:
      outfile.write(json.dumps(settings,indent=4))
    
    
  def initUI(self):

    SkopePanelFactory.registerOperatorsPanel(self.type)
    SkopePanelFactory.registerSettingsPanel("skope",self.settings)
    SkopePanelFactory.registerSettingsPanel("cone",self.state.cone.settings)
    SkopePanelFactory.registerSettingsPanel("screen",self.state.screen.settings)
    SkopePanelFactory.registerSettingsPanel("camera",self.state.camera.settings)

    for area in bpy.context.screen.areas:
      if area.type == 'VIEW_3D':
          with bpy.context.temp_override(
              area=area,
              window=bpy.context.window,
              region=[region for region in area.regions if region.type == 'WINDOW'][0],
              screen=bpy.context.window.screen
          ):
              bpy.context.space_data.shading.type = 'RENDERED'
              bpy.context.space_data.show_region_ui = True
              bpy.ops.view3d.camera_to_view()
              bpy.ops.screen.screen_full_area()
          break
    

  def create_clip(self, length):
    print("Skope create_clip", length)
    scene = bpy.context.scene
    scene.frame_end = length # +-1 ?
    scene.frame_set(1)
    self.clip = SkopeClip(scene,length)
    self.clip.apply(scene)
    filename = scene.skope.state.id
    scene.render.filepath = self.settings.fixed['output_dir']+ '/' + filename
    
  ## --------- RENDER MODE -------------- ##

  def render_stills(self, amount): 
    print("Rendering random stills ..")
    scene = bpy.context.scene
    ofp = scene.render.filepath
    orp = scene.render.resolution_percentage
    oif = scene.render.image_settings.file_format
    scene.render.resolution_percentage = self.settings.fixed['scale']
    scene.render.image_settings.file_format = self.settings.fixed['image_format']
    for frame in range(0,amount):
      self.state.random()
      self.render_still(scene)
    scene.render.filepath = ofp
    scene.render.resolution_percentage = orp
    scene.render.image_settings.file_format = oif
    print("Rendering done.")

  def render_still(self,scene,filepath=None): 
    self.state.apply(scene)
    if not filepath:
      filepath = self.settings.fixed['output_dir']+ '/' + self.state.id
    else:
      filepath = os.path.splitext(filepath)[0]
    scene.render.filepath = filepath
    print("Rendering",scene.render.filepath)
    self.frozen = True
    self.state.writeJSON(scene.render.filepath +'.json')
    bpy.ops.render.render(write_still=True) # render still
    self.frozen = False

  def render_clips(self,length,amount=1):
    # create a random clip and step it every frame
    self.create_clip(int(length))
    self.clip.random()
    scene = bpy.context.scene
    ofp = scene.render.filepath
    orp = scene.render.resolution_percentage
    oif = scene.render.image_settings.file_format
    scene.render.resolution_percentage = self.settings.fixed['scale']
    scene.render.image_settings.file_format = self.settings.fixed['video_format']
    scene.render.ffmpeg.format=self.settings.fixed['ffmpeg_format']
    # scene.render.ffmpeg.codec
    # scene.render.ffmpeg.ffmpeg_preset
    # ...
    
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(self.apply_clip_step)
    self.rendering = True
    while amount > 0:
      self.render_clip(scene)
      amount = amount - 1
      self.clip.next_delta()
      bpy.context.scene.frame_set(0)

    self.rendering = False
    scene.render.filepath = ofp
    scene.render.resolution_percentage = orp
    scene.render.image_settings.file_format = oif
    print("Rendering done.")

  def render_clip(self,scene,filepath=None): 
    if not filepath:
      filepath = self.settings.fixed['output_dir']+ '/' + self.clip.id
    else:
      filepath = os.path.splitext(filepath)[0]
    #scene.render.filepath = filepath
    #filename = self.clip.id;
    scene.render.filepath = filepath + '-'
    print("Rendering",scene.render.filepath)
    self.frozen = True
    self.clip.writeJSON(filepath +'.json')
    bpy.ops.render.render(animation=True) # render animation
    self.frozen = False
  
  def render_loops(self,length,amount=2.0):
    # a loop is a collection of clips, where the endstate
    # of every clip is the beginstate of another clip, so
    # you are garantueed to be able to loop whereever
    # you are. skope will look at the existing clips 
    # in the output dir and randomly create new clips tying
    # existing clips together. it also randomly creates 
    # new clips starting with an existing endstate.
    # you have to pass an even amount in order for at 
    # least every new clip to be available in reverse.

    scene = bpy.context.scene
    scene.frame_end = length # +-1 ?
    scene.frame_set(1)
    self.clip = SkopeClip(scene,length)

    ofp = scene.render.filepath
    orp = scene.render.resolution_percentage
    oif = scene.render.image_settings.file_format
    scene.render.resolution_percentage = self.settings.fixed['scale']
    scene.render.image_settings.file_format = self.settings.fixed['video_format']
    scene.render.ffmpeg.format=self.settings.fixed['ffmpeg_format']
    # scene.render.ffmpeg.codec
    # scene.render.ffmpeg.ffmpeg_preset
    # ...

    # make amount even
    amount = math.ceil(amount/2.0)*2

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(self.apply_clip_step)
    self.rendering = True
    while amount > 0:
        #   glob output dir for jsons
        clips = []
        pattern = '([0-9a-z]+)-([0-9a-z]+)\.json'
        for file in os.listdir(self.settings.fixed['output_dir']):
            match = re.match(pattern,file)
            if match:
                with open(self.settings.fixed['output_dir']+'/'+file, "r") as infile:
                  clips.append({
                      'file': file,
                      'start_state': match.group(1),
                      'end_state': match.group(2),
                      'data': json.load(infile)
                  })
        print("Found clips",[clip['file'] for clip in clips])

        if not len(clips):   
            print("creating random clip")
            self.create_clip(int(length))
            self.clip.random()
            self.render_clip(scene)
            amount = amount - 1
            self.clip.reverse()
            print("creating reverse clip",self.clip.id)
            self.render_clip(scene)
            amount = amount - 1
            continue

        #   take random end state
        rnd_clip = random.choice(clips)
        
        reverse_clips = [
              clip for clip in clips if clip['start_state'] == rnd_clip['end_state']
                and clip['end_state'] == rnd_clip['start_state']
        ]
        if not len(reverse_clips) and random.random()<self.settings.loop['loop_reverse_chance']:
          # always create a reverse if it is missing
          self.clip.fromJSON({
            'id' : rnd_clip['end_state']+'-'+rnd_clip['start_state'],
            'src': rnd_clip['data']['dst'],
            'dst' : rnd_clip['data']['src']
          })
          print("creating reverse",self.clip.id)
          print()
          self.render_clip(scene)
          amount = amount - 1
          continue  
        
        end_state = rnd_clip['end_state']
        end_data = rnd_clip['data']['dst']
        print("using end state",end_state,"as start")

        if not random.random()<self.settings.loop['loop_branch_chance']:
            # find one random clip from end_state to start_state
            # that does *not* exist yet and create that
            existing_end_states = [
              clip['end_state'] for clip in clips if clip['start_state'] == end_state
            ]
            print("existing end states starting with",end_state,existing_end_states)
            missing_start_clips = [
              clip for clip in clips if clip['start_state'] not in existing_end_states 
              and clip['start_state'] != end_state
            ]
            if len(missing_start_clips):
                print("found missing start states",[
                  clip['start_state'] for clip in missing_start_clips
                ])
                random.shuffle(missing_start_clips)
                start_clip = missing_start_clips[0]
                start_state = start_clip['start_state']
                start_data = start_clip['data']['src']
                # check your logic
                # existing_clips = [clip for clip in clips if clip['start_state']==end_state and clip['end_state']==start_state]
                #if len(existing_clips):
                #  print("fail: that already exists. Exiting.")
                #  exit
                self.clip.fromJSON({
                  'id' : end_state+'-'+start_state,
                  'src': end_data,
                  'dst' : start_data
                })
                print("creating",self.clip.id)
                print()
                self.render_clip(scene)
                amount = amount - 1
                continue
            else:
                print("no missing startstates")
                
        else:
            print("randomly creating new branch")

        # create a new clip with this end_state as start
        # and a random end_state, and create the reverse clip
        self.clip.fromJSON({
          'id' : end_state+'-'+end_state,
          'src': end_data,
          'dst' : end_data
        })
        self.clip.next_delta()
        print("render new endstate",self.clip.id)
        self.render_clip(scene)
        amount = amount - 1
        self.clip.reverse()
        print("creating reverse clip",self.clip.id)
        self.render_clip(scene)
        amount = amount - 1
    self.rendering = False
    scene.render.filepath = ofp
    scene.render.resolution_percentage = orp
    scene.render.image_settings.file_format = oif
    print("Rendering done.")
    
  ## --------- REGENERATE MODE -------------- ##
  
  
  def regenerate_stills(self): 
    print("Regenerating selected json files ..")
    state_files=glob.glob(self.settings.fixed['import_dir']+'/*.json')
    scene = bpy.context.scene
    ofp = scene.render.filepath
    orp = scene.render.resolution_percentage
    oif = scene.render.image_settings.file_format
    scene.render.resolution_percentage = self.settings.fixed['scale']
    scene.render.image_settings.file_format = self.settings.fixed['image_format']
    
    for state_file in state_files:
      self.regenerate_still(state_file,scene)
    scene.render.filepath = ofp
    scene.render.resolution_percentage = orp
    scene.render.image_settings.file_format = oif
    print("Regenerating done.")
    
  def regenerate_still(self,file,scene): 
    basename = os.path.splitext(os.path.basename(file))[0]
    self.state.readJSON(file)
    self.state.apply(scene)
    scene.render.filepath = self.settings.fixed['output_dir'] + '/' + basename
    print("Regenerating",file)
    bpy.ops.render.render(write_still=True) # render still
    self.state.writeJSON(scene.render.filepath+'.json');
  
  def regenerate_clips(self,length): 
    print("Regenerating selected json files ..")
    clip_files=glob.glob(self.settings.fixed['import_dir']+'/*-*.json')
    scene = bpy.context.scene
    scene.frame_end = length # +-1 ?
    scene.frame_set(1)
    self.clip = SkopeClip(scene,length)
    ofp = scene.render.filepath
    orp = scene.render.resolution_percentage
    oif = scene.render.image_settings.file_format
    scene.render.resolution_percentage = self.settings.fixed['scale']
    scene.render.image_settings.file_format = self.settings.fixed['video_format']
    scene.render.ffmpeg.format=self.settings.fixed['ffmpeg_format']
    # scene.render.ffmpeg.codec
    # scene.render.ffmpeg.ffmpeg_preset
    # ...

    self.rendering = True
    for clip_file in clip_files:
      self.regenerate_clip(clip_file,scene)
    self.rendering = False

    scene.render.filepath = ofp
    scene.render.resolution_percentage = orp
    scene.render.image_settings.file_format = oif
    print("Regenerating done.")
    
  def regenerate_clip(self,file,scene):  ##~~
    self.clip.readJSON(file)
    self.clip.apply(scene)
    self.render_clip(scene)
    
  ## --------- EVENT HANDLERS -------------- ##
  
  #def apply_random_filepath(self,scene,x):
  #  print("apply_random_filepath")
  #  filename = str(uuid.uuid4())[:4]+'-';
  #  scene.render.filepath = self.settings.fixed['output_dir']+ '/' + filename

  def apply_random_state(self,scene,x=0):
    if not self.frozen:
      print("apply_random_state",scene.frame_current)
      #bpy.types.RenderSettings.use_lock_interface = True
      #bpy.context.scene.render.use_lock_interface = True
      #SkopeState.frame_num = scene.frame_current
      self.state.random()
      self.state.apply(scene)

  def apply_clip_step(self,scene,x=0):
    print("apply_clip_step")
    # try colect garbage every frame ... slow 
    # gc.collect()
    if (not self.rendering) and scene.frame_current >= self.clip.length :
      self.clip.next_delta()
      bpy.context.scene.frame_set(0)
    else :
      self.clip.go(scene.frame_current)
      #bpy.types.RenderSettings.use_lock_interface = True
      #bpy.context.scene.render.use_lock_interface = True
      self.clip.apply(scene)

  def apply_start_render(self,scene,x=0):
    self.rendering = True

  def apply_stop_render(self,scene,x=0):
    self.rendering = False

  def freeze(self,scene,x=0):
    print("freeze")
    self.frozen = True

  def unfreeze(self,scene,x=0):
    print("unfreeze")
    self.frozen = False
      
