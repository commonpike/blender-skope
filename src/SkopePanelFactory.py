# SkopePanelFactory 
# 
# contains static methods
# to generate and register propertygroup-, 
# panel- and operator-classes
# that can modify settings objects

import bpy
from easings import getEasings
from distributions import getDistributions

class SkopePanelFactory():

    # createSettingsPanel creates subclasses of the 
    # SkopePropertyGroup and the SkopeSettingsPanel
    # and registers those classes. Each settings object
    # has one propertygroup and multiple panels in one 
    # category

    def registerSettingsPanel(target, settings):

        classid = target.title()
        label = target.title()

        # create property group
        properties_id = 'skope_properties_'+target
        properties = type('SkopePropertyGroup'+classid, (SkopePropertyGroup,), {})
        properties.init(target,settings)
        bpy.utils.register_class(properties)
        setattr(bpy.types.Scene,properties_id,bpy.props.PointerProperty(type=properties))

        
        # create panels to display properties in each key
        for key in settings:
            if not key.startswith('_') and isinstance(settings[key], dict):
                panel = type('VIEW3D_PT_SettingsPanel'+classid+key.title(), (SkopeSettingsPanel,), {
                    'bl_category': label,
                    'bl_label': label+' '+key,
                    'bl_order': 2,
                    'properties_id': properties_id,
                    'target': target,
                    'settings': settings,
                    'key': key
                })        
                bpy.utils.register_class(panel)

    def registerOperatorsPanel():
        bpy.utils.register_class(SkopeStepOperator)
        bpy.utils.register_class(SkopeSaveOperator)
        bpy.utils.register_class(SkopeLoadOperator)
        bpy.utils.register_class(SkopeResetOperator)
        bpy.utils.register_class(SkopeRandomOperator)
        bpy.utils.register_class(SkopeDeltaOperator)
        bpy.utils.register_class(SkopeResetClipOperator)
        bpy.utils.register_class(SkopeRandomClipOperator)
        bpy.utils.register_class(SkopeDeltaClipOperator)
        bpy.utils.register_class(VIEW3_PT_skope_operators)



# A SkopePropertyGroup represents all of the 
# entries in a SkopeSettings object. The 'target'
# is the object (SkopeScreen, SkopeCamera, etc) the
# settings belong to. 

class SkopePropertyGroup(bpy.types.PropertyGroup):
    target = None
    settings = {}
    properties = {}

    @classmethod
    def getter(cls,key,propname,items=None):
        def method(self):
            if not items:
                return cls.target.settings[key][propname]
            else:
                value = cls.target.settings[key][propname]
                for i in range(len(items)):
                    #print(i,items[i])
                    if items[i][0] == value:
                        return i
                return 0
        return method

    @classmethod
    def setter(cls,key,propname,items=None):
        def method(self,value):
            if not items:
                cls.target.settings[key][propname]=value
            else:
                cls.target.settings[key][propname]=items[value][0]
        return method

    @classmethod
    def init(cls,target,settings):
        if target != 'skope':
            cls.target = getattr(bpy.context.scene.skope.state,target,None)
        else:
            cls.target = bpy.context.scene.skope
        if cls.target is None:
            raise Exception("Failed to refer SkopePropertyGroup to target "+target)
        cls.settings2properties(settings)

    @classmethod
    def settings2properties(cls,settings):
        for key in settings:
            if not key.startswith('_'):
                if isinstance(settings[key], dict):
                    for propname in settings[key]:
                        cls.setting2property(settings,key,propname)

    @classmethod
    def setting2property(cls,settings,key,propname=''):
        propid = key+'_'+propname
        config = {
            'name': propname,
            'get' : cls.getter(key,propname),
            'set' : cls.setter(key,propname),
        }
        if isinstance(settings[key][propname],bool):
            cls.__annotations__[propid] = bpy.props.BoolProperty(**config)
        elif isinstance(settings[key][propname],int):
            cls.__annotations__[propid] = bpy.props.IntProperty(**config)
        elif isinstance(settings[key][propname],float):
            if propname.startswith('rotation') or propname.endswith('rotation'):
                cls.__annotations__[propid] = bpy.props.FloatProperty(
                    subtype="ANGLE",
                    **config
                )
            elif (key.startswith('rotation') 
                  or key.endswith('rotation')
                ) and (propname in [
                    'default','minimum','maximum','x','y','z'
                ]):
                cls.__annotations__[propid] = bpy.props.FloatProperty(
                    subtype="ANGLE",
                    **config
                )
            else:
                cls.__annotations__[propid] = bpy.props.FloatProperty(**config)
        elif isinstance(settings[key][propname],str):
            if propname == 'easing':
                items = []
                for easing in getEasings():
                    items.append((easing,easing,easing))
                cls.__annotations__[propid] = bpy.props.EnumProperty(
                    name = propname,
                    items = items,
                    get = cls.getter(key,propname,items),
                    set = cls.setter(key,propname,items),
                )
            elif propname == 'distribution':
                items = []
                for distribution in getDistributions():
                    items.append((distribution,distribution,distribution))
                cls.__annotations__[propid] = bpy.props.EnumProperty(
                    name = propname,
                    items = items,
                    get = cls.getter(key,propname,items),
                    set = cls.setter(key,propname,items),
                )
            elif propname == 'directory' or propname.endswith('_dir'):
                cls.__annotations__[propid] = bpy.props.StringProperty(
                    subtype='DIR_PATH',
                    **config
                )
        
            else:
                cls.__annotations__[propid] = bpy.props.StringProperty(**config)
        

# Each SkopeSettingsPanel only refers to the properties of 
# single key within a targets settings, eg 
# Screen > location_x > *
# It uses the settings property group to modify these 
# values through the getters and setters there.

class SkopeSettingsPanel(bpy.types.Panel):  

    # where to add the panel in the UI
    bl_space_type = "VIEW_3D"  
    bl_region_type = "UI"  
    bl_options = {"DEFAULT_CLOSED"}

    # add labels
    bl_category = "-- undefined --"  
    bl_label = "-- undefined --" 
    
    properties_id = "none"
    target = "none"
    settings = {}
    key = "none"

    def draw(self, context):
        properties = getattr(context.scene,self.properties_id)
        for propname in self.settings[self.key]:
            propid = self.key+"_"+propname
            self.layout.prop(properties, propid)


        

# Operators & operator panel

class SkopeStepOperator(bpy.types.Operator):
    bl_idname = "scene.skope_step_operator"
    bl_label = "Step"

    def execute(self, context):
        scene = context.scene
        scene.frame_set(scene.frame_current + 1)
        return {'FINISHED'}

class SkopeLoadOperator(bpy.types.Operator):
    bl_idname = "scene.skope_load_operator"
    bl_label = "Load"

    def execute(self, context):
        print("Load settings not implemented")
        return {'CANCELLED'}
     
class SkopeSaveOperator(bpy.types.Operator):
    bl_idname = "scene.skope_save_operator"
    bl_label = "Save"

    def execute(self, context):
        print("Save settings not implemented")
        return {'CANCELLED'}

class SkopeResetOperator(bpy.types.Operator):
    bl_idname = "scene.skope_reset_operator"
    bl_label = "Reset"

    def execute(self, context):
        scene = context.scene
        skope = scene.skope
        skope.reset(True)
        return {'FINISHED'}
    
class SkopeRandomOperator(bpy.types.Operator):
    bl_idname = "scene.skope_random_operator"
    bl_label = "Random"

    def execute(self, context):
        scene = context.scene
        skope = scene.skope
        skope.state.random()
        skope.state.apply(scene)
        return {'FINISHED'}
    
class SkopeDeltaOperator(bpy.types.Operator):
    bl_idname = "scene.skope_delta_operator"
    bl_label = "Delta"

    def execute(self, context):
        scene = context.scene
        skope = scene.skope
        skope.state.rnd_delta()
        skope.state.apply(scene)
        return {'FINISHED'}
    
class SkopeResetClipOperator(bpy.types.Operator):
    bl_idname = "scene.skope_reset_clip_operator"
    bl_label = "Reset Clip"

    def execute(self, context):
        scene = context.scene
        skope = scene.skope
        if hasattr(skope,'clip'):
            skope.clip.reset()
            skope.clip.apply(scene)
            return {'FINISHED'}
        return {'CANCELLED'}
    
class SkopeRandomClipOperator(bpy.types.Operator):
    bl_idname = "scene.skope_random_clip_operator"
    bl_label = "Random Clip"

    def execute(self, context):
        scene = context.scene
        skope = scene.skope
        if hasattr(skope,'clip'):
            skope.clip.random()
            skope.clip.apply(scene)
            return {'FINISHED'}
        return {'CANCELLED'}
    
class SkopeDeltaClipOperator(bpy.types.Operator):
    bl_idname = "scene.skope_delta_clip_operator"
    bl_label = "Delta Clip"

    def execute(self, context):
        scene = context.scene
        skope = scene.skope
        if hasattr(skope,'clip'):
            skope.clip.next_delta()
            skope.clip.apply(scene)
            return {'FINISHED'}
        return {'CANCELLED'}


class VIEW3_PT_skope_operators(bpy.types.Panel):  

    # where to add the panel in the UI
    bl_space_type = "VIEW_3D"  
    bl_region_type = "UI"  
    bl_order = 1
    #bl_options = {"DEFAULT_CLOSED"}
    #use_pin = True - doesnt pin

    # add labels
    bl_category = "Operators"  
    bl_label = "Skope operators" 
    
    def draw(self, context):
        
        row = self.layout.row()
        split = row.split()
        col = split.column()
        if not context.scene.skope.clip:
            col.operator(SkopeResetOperator.bl_idname)
        else:
            col.operator(SkopeResetClipOperator.bl_idname)
        col = split.column()
        col.operator(SkopeStepOperator.bl_idname)
        
        row = self.layout.row()
        split = row.split()
        if not context.scene.skope.clip:
            col = split.column()
            col.operator(SkopeRandomOperator.bl_idname)
            col = split.column()
            col.operator(SkopeDeltaOperator.bl_idname)
        else:            
            col = split.column()
            col.operator(SkopeRandomClipOperator.bl_idname)
            col = split.column()
            col.operator(SkopeDeltaClipOperator.bl_idname)

        row = self.layout.row()
        split = row.split()
        col = split.column()
        col.operator(SkopeLoadOperator.bl_idname)
        col = split.column()
        col.operator(SkopeSaveOperator.bl_idname)


       