# This file contains settings and functions the users texture set.

import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, StringProperty, PointerProperty, FloatVectorProperty, EnumProperty
from ..core import blender_addon_utils

# Available texture resolutions for texture sets.
TEXTURE_SET_RESOLUTIONS = [
    ("FIVE_TWELVE", "512", ""), 
    ("ONEK", "1024", ""),
    ("TWOK", "2048", ""),
    ("FOURK", "4096", ""),
]

def update_match_image_resolution(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return
    
    texture_set_settings = context.scene.matlayer_texture_set_settings
    if texture_set_settings.match_image_resolution:
        texture_set_settings.image_height = texture_set_settings.image_width

def update_image_width(self, context):
    if context.scene.matlayer_texture_set_settings.auto_update_properties == False:
        return

    texture_set_settings = context.scene.matlayer_texture_set_settings
    if texture_set_settings.match_image_resolution:
        if texture_set_settings.image_height != texture_set_settings.image_width:
            texture_set_settings.image_height = texture_set_settings.image_width

#----------------------------- UPDATE GLOBAL MATERIAL CHANNEL TOGGLES (mute / unmute material channels for ALL layers) -----------------------------#

def get_texture_width():
    '''Returns a numeric value based on the enum for texture width.'''
    match bpy.context.scene.matlayer_texture_set_settings.image_width:
        case 'FIVE_TWELVE':
            return 512
        case 'ONEK':
            return 1024
        case 'TWOK':
            return 2048
        case 'FOURK':
            return 4096
        case _:
            return 10

def get_texture_height():
    '''Returns a numeric value based on the enum for texture height.'''
    match bpy.context.scene.matlayer_texture_set_settings.image_height:
        case 'FIVE_TWELVE':
            return 512
        case 'ONEK':
            return 1024
        case 'TWOK':
            return 2048
        case 'FOURK':
            return 4096
        case _:
            return 10

def get_material_channel_active(material_channel_name):
    '''Returns if the material channel is active in the active materials texture set.'''
    if not bpy.context.active_object:
        return
    
    active_material = bpy.context.active_object.active_material
    if not active_material:
        return
    
    material_channel_toggle_node = active_material.node_tree.nodes.get("GLOBAL_{0}_TOGGLE".format(material_channel_name))

    if material_channel_toggle_node.mute:
        return False
    else:
        return True

class MATLAYER_texture_set_settings(PropertyGroup):
    image_width: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Image Width", description="Image width in pixels for the new image.", default='TWOK', update=update_image_width)
    image_height: EnumProperty(items=TEXTURE_SET_RESOLUTIONS, name="Image Height", description="Image height in pixels for the new image.", default='TWOK')
    layer_folder: StringProperty(default="", description="Path to folder location where layer images are saved", name="Image Layer Folder Path")
    match_image_resolution: BoolProperty(name="Match Image Resolution", description="When toggled on, the image width and height will be matched", default=True, update=update_match_image_resolution)
    thirty_two_bit: BoolProperty(name="32 Bit Color", description="When toggled on, images created using this add-on will be created with 32 bit color depth. 32-bit images will take up more memory, but will have significantly less color banding in gradients. On monitors (generally older or cheap ones) that don't support this color depth there will be no visual difference", default=True)

class MATLAYER_OT_toggle_texture_set_material_channel(Operator):
    bl_idname = "matlayer.toggle_texture_set_material_channel"
    bl_label = "Toggle Texture Set Material Channel"
    bl_description = "Toggles the specified material channel on / off for the active materials texture set"
    bl_options = {'REGISTER', 'UNDO'}

    material_channel_name: StringProperty(default='COLOR')

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        blender_addon_utils.verify_material_operation_context(self)
        active_material = bpy.context.active_object.active_material
        channel_toggle_node = active_material.node_tree.nodes.get("GLOBAL_{0}_TOGGLE".format(self.material_channel_name))
        if channel_toggle_node.mute:
            channel_toggle_node.mute = False
        else:
            channel_toggle_node.mute = True
        return {'FINISHED'}