# This file contains settings and functions the users texture set.

import os
import bpy
from bpy.types import PropertyGroup, Operator
from bpy.props import BoolProperty, StringProperty, EnumProperty
from ..core import blender_addon_utils as bau
from ..core import debug_logging

# Available texture resolutions for texture sets.
TEXTURE_SET_RESOLUTIONS = [
    ("THIRTY_TWO", "32", ""),
    ("SIXTY_FOUR", "64", ""),
    ("ONE_TWENTY_EIGHT", "128", ""),
    ("TWO_FIFTY_SIX", "256", ""),
    ("FIVE_TWELVE", "512", ""),
    ("ONE_K", "1024", ""),
    ("TWO_K", "2048", ""),
    ("FOUR_K", "4096", "")
]

def update_match_image_resolution(self, context):
    texture_set_settings = context.scene.rymat_texture_set_settings
    if texture_set_settings.match_image_resolution:
        texture_set_settings.image_height = texture_set_settings.image_width

def update_image_width(self, context):
    texture_set_settings = context.scene.rymat_texture_set_settings
    if texture_set_settings.match_image_resolution:
        if texture_set_settings.image_height != texture_set_settings.image_width:
            texture_set_settings.image_height = texture_set_settings.image_width

#----------------------------- UPDATE GLOBAL MATERIAL CHANNEL TOGGLES (mute / unmute material channels for ALL layers) -----------------------------#

def get_texture_width():
    '''Returns a numeric value based on the enum for texture width.'''
    match bpy.context.scene.rymat_texture_set_settings.image_width:
        case 'THIRTY_TWO':
            return 32
        case 'SIXTY_FOUR':
            return 64
        case 'ONE_TWENTY_EIGHT':
            return 128
        case 'TWO_FIFTY_SIX':
            return 256
        case 'FIVE_TWELVE':
            return 512
        case 'ONE_K':
            return 1024
        case 'TWO_K':
            return 2048
        case 'FOUR_K':
            return 4096
        case _:
            return 10

def get_texture_height():
    '''Returns a numeric value based on the enum for texture height.'''
    match bpy.context.scene.rymat_texture_set_settings.image_height:
        case 'THIRTY_TWO':
            return 32
        case 'SIXTY_FOUR':
            return 64
        case 'ONE_TWENTY_EIGHT':
            return 128
        case 'TWO_FIFTY_SIX':
            return 256
        case 'FIVE_TWELVE':
            return 512
        case 'ONE_K':
            return 1024
        case 'TWO_K':
            return 2048
        case 'FOUR_K':
            return 4096
        case _:
            return 10

class RYMAT_texture_set_settings(PropertyGroup):
    image_width: EnumProperty(
        items=TEXTURE_SET_RESOLUTIONS, 
        name="Image Width", 
        description="Image width in pixels for all images created with this add-on. Changing this value during through creating a material could result in the pixel resolution between textures used in the material not matching, which will cause exported textures to be blurry", 
        default='TWO_K', 
        update=update_image_width
    )

    image_height: EnumProperty(
        items=TEXTURE_SET_RESOLUTIONS, 
        name="Image Height", 
        description="Image height in pixels for all images created with this add-on. Changing this value during through creating a material could result in the pixel resolution between textures used in the material not matching, which will cause exported textures to be blurry", 
        default='TWO_K'
    )

    layer_folder: StringProperty(default="", description="Path to folder location where layer images are saved", name="Image Layer Folder Path")
    match_image_resolution: BoolProperty(name="Match Image Resolution", description="When toggled on, the image width and height will be matched", default=True, update=update_match_image_resolution)

class RYMAT_OT_set_raw_texture_folder(Operator):
    bl_idname = "rymat.set_raw_texture_folder"
    bl_label = "Set Raw Texture Folder Path"
    bl_description = "Opens a file explorer to select the folder path where raw textures are externally saved. A raw texture is any image used in the material editing process inside this add-on that isn't a texture being exported"
    bl_options = {'REGISTER'}

    directory: StringProperty()

    # Filters for only folders.
    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}
    )

    def execute(self, context):
        if not os.path.isdir(self.directory):
            debug_logging.log_status("Invalid directory.", self, type='INFO')
        else:
            context.scene.rymat_raw_textures_folder = self.directory
            debug_logging.log_status("Raw texture folder set to: {0}".format(self.directory), self, type='INFO')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class RYMAT_OT_open_raw_texture_folder(Operator):
    bl_idname = "rymat.open_raw_texture_folder"
    bl_label = "Open Raw Texture Folder"
    bl_description = "Opens the folder in your systems file explorer where raw textures will be saved. Raw textures are considered any image that's used in the material editing process, that's not a mesh map, or a completed texture being exported"

    # Disable when there is no active object.
    @ classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        raw_texture_folder_path = bau.get_texture_folder_path(folder='RAW_TEXTURES')
        bau.open_folder(raw_texture_folder_path, self)
        return {'FINISHED'}