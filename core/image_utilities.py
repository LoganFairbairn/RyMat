# This file provides functions to assist with importing, saving, or editing image files / textures for this add-on.

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from ..core import texture_set_settings as tss
from ..core import debug_logging
from ..core import blender_addon_utils as bau
from ..core import shaders
from .. import preferences
import random
import os
import shutil

def get_random_image_id():
    '''Generates a random image id number.'''
    return str(random.randrange(10000,99999))

def set_default_image_colorspace(image, material_channel_name):
    '''Sets an image's default colorspace based on the shader settings for the specified material channel.'''
    shader_info = bpy.context.scene.rymat_shader_info
    channel_socket_name = shaders.get_shader_channel_socket_name(material_channel_name)
    material_channel = shader_info.material_channels.get(channel_socket_name)
    if material_channel:
        image.colorspace_settings.name = material_channel.default_colorspace
    else:
        debug_logging.log(
            "Failed to set default image colorspace, no material channel {0}".format(material_channel_name),
            message_type='ERROR',
            sub_process=False
        )

def check_for_directx(filename):
    if "NormalDX" in filename or "NDX" in filename:
        return True
    else:
        return False

def save_raw_image(original_image_path, original_image_name):
    '''Saves an imported image to a folder where raw, unprocessed textures are stored. This can help keep textures used in materials within the blend file in a static location next to the blend file for organizational purposes.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    if addon_preferences.save_imported_textures:

        debug_logging.log("Attempting to copy the imported texture into the raw textures folder.")
        
        # In some cases, the original image name may include the file extension of the image already. 
        # We'll remove this to avoid saving images with the file extension in the name.
        rymat_raw_textures_folder_path = bau.get_texture_folder_path(folder='RAW_TEXTURES')
        original_image_name_extension = os.path.splitext(original_image_name)[1]
        if original_image_name_extension:
            original_image_name = original_image_name.replace(original_image_name_extension, '')

        # Save the raw texture in a folder next to the saved blend file if it doesn't exist within that folder.
        original_file_format = os.path.splitext(original_image_path)
        destination_path = "{0}/{1}{2}".format(rymat_raw_textures_folder_path, original_image_name, original_file_format[1])
        if not os.path.exists(destination_path):
            shutil.copyfile(original_image_path, destination_path)
            debug_logging.log("Imported image copied to the raw texture folder.")
        debug_logging.log("Imported image already exists within the raw texture folder.")

def save_all_textures():
    '''Saves all unsaved image textures in the blend file (using default save method in texture settings)'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences

    # If the default save method is pack,
    # pack all images in the blend file that have no filepath, and unsaved data.
    if addon_preferences.default_texture_save_method == 'PACK':
        for image in bpy.data.images:
            if image.filepath == '' and image.is_dirty and image.has_data:
                image.pack()

    # If the default save method if saving externally, trigger a save
    # for all images that have a defined filepath and unsaved data..
    else:
        for image in bpy.data.images:
            if image.filepath == '' and image.is_dirty and image.has_data:
                image.save()
    
def auto_save_images():
    '''Auto-saves all images in the blend file that are dirty and have defined paths.'''
    addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
    if addon_preferences.auto_save_images:

        # To avoid errors with saving and baking textures at the same time, only run auto-save when there is no baking in progress.
        if not bpy.app.is_job_running('OBJECT_BAKE'):
            save_all_textures()
            debug_logging.log("Auto-saved all images.", message_type='INFO', sub_process=False)

        # Return the time until the auto-save should be called again.
        return addon_preferences.image_auto_save_interval
    
    # Return None to unregister the timer (effecitvely stops image auto saving).
    return None

class RYMAT_OT_save_all_textures(Operator):
    bl_idname = "rymat.save_all_textures"
    bl_label = "Save All Textures"
    bl_description = "Saves all unsaved image textures in the blend file (using default save method in texture settings)"

    def execute(self, context):
        save_all_textures()
        debug_logging.log_status("Saved all images.", self, type='INFO')
        return {'FINISHED'}

class RYMAT_OT_add_texture_node_image(Operator):
    bl_idname = "rymat.add_texture_node_image"
    bl_label = "Add Texture Node Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates a new image (uses texture set pixel resolution) and adds it to the specified texture node"

    node_tree_name: StringProperty(default="", options={'HIDDEN'})
    node_name: StringProperty(default="", options={'HIDDEN'})
    material_channel_name: StringProperty(default="", options={'HIDDEN'})

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        # Assign the new image a random name.
        image_name = "Image_" + get_random_image_id()
        while bpy.data.images.get(image_name) != None:
            image_name = "Image_" + get_random_image_id()

        # Create a new image of the texture size defined in the texture set settings.
        addon_preferences = bpy.context.preferences.addons[preferences.ADDON_NAME].preferences
        image_width = tss.get_texture_width()
        image_height = tss.get_texture_height()
        new_image = bau.create_image(
            image_name, 
            image_width, 
            image_height,
            base_color=[0.0, 0.0, 0.0, 0.0],
            alpha_channel=True, 
            thirty_two_bit=addon_preferences.thirty_two_bit
        )
    
        # If a material channel is defined, set the color space.
        if self.material_channel_name != "":
            set_default_image_colorspace(new_image, self.material_channel_name)

        # Add the new image to the image node.
        texture_node.image = new_image

        # Select the new texture for painting.
        bau.set_texture_paint_image(new_image)
        
        return {'FINISHED'}

class RYMAT_OT_import_texture_node_image(Operator, ImportHelper):
    bl_idname = "rymat.import_texture_node_image"
    bl_label = "Import Texture"
    bl_description = "Opens a menu that allows the user to import a texture file into the specified texture node"
    bl_options = {'REGISTER', 'UNDO'}

    node_tree_name: StringProperty(default="", options={'HIDDEN'})
    node_name: StringProperty(default="", options={'HIDDEN'})
    material_channel_name: StringProperty(default="", options={'HIDDEN'})

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp;*.exr',
        options={'HIDDEN'}
    )

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        # Open a window to import an image into blender.
        head_tail = os.path.split(self.filepath)
        image_name = head_tail[1]

        # To avoid users importing the same image twice, if the image already exists, throw an error.
        image = bpy.data.images.get(image_name)
        if image:
            debug_logging.log_status("Failed to import image. An image with the same name already exists in blend data.", self, type='ERROR')
            return {'CANCELLED'}
            
        bpy.ops.image.open(filepath=self.filepath)
        image = bpy.data.images[image_name]
        texture_node.image = image
        
        # If a material channel is defined, set the color space.
        if self.material_channel_name != "":
            set_default_image_colorspace(image, self.material_channel_name)
            shader_info = bpy.context.scene.rymat_shader_info
            channel_socket_name = shaders.get_shader_channel_socket_name(self.material_channel_name)
            material_channel = shader_info.material_channels.get(channel_socket_name)
            if material_channel:
                texture_node.interpolation = material_channel.default_texture_interpolation

        # Print a warning about using DirectX normal maps for users if it's detected they are using one.
        if check_for_directx(image_name) and self.material_channel_name == 'NORMAL':
            debug_logging.log_status("You may have imported a DirectX normal map which will cause your imported normal map to appear inverted.", self, type='WARNING')

        # Copy the imported image to a folder next to the blend file (if save imported textures is on in the settings).
        save_raw_image(self.filepath, image.name)
        return {'FINISHED'}

class RYMAT_OT_edit_texture_node_image_externally(Operator):
    bl_idname = "rymat.edit_texture_node_image_externally"
    bl_label = "Edit Image Externally"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Exports the specified material channel image to the external image editing software defined in Blenders preferences"

    node_tree_name: StringProperty(default="", options={'HIDDEN'})
    node_name: StringProperty(default="", options={'HIDDEN'})

    def execute(self, context):
        image_editor_path = bpy.context.preferences.filepaths.image_editor
        if not image_editor_path:
            debug_logging.log_status("Image editor path isn't defined.", self, type='ERROR')
            return {'CANCELLED'}

        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status(
                "Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", 
                self, 
                type='ERROR'
            )
            return {'CANCELLED'}

        if self.node_name == "":
            debug_logging.log_status(
                "Provided texture node name is blank when attempting to import a texture to a texture node.", 
                self, 
                type='ERROR'
            )
            return {'CANCELLED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status(
                "Can't find the specified texture node when attempting to import a texture to a texture node.", 
                self, 
                type='ERROR'
            )
            return {'CANCELLED'}
        
        if texture_node.image == None:
            debug_logging.log_status(
                "No image to edit externally.",
                self,
                type='ERROR'
            )
            return {'CANCELLED'}

        if bau.check_blend_saved() == False:
            debug_logging.log_status(
                "Please save your blend file to use this operator.", 
                self, 
                type='ERROR'
            )
            return {'FINISHED'}

        # If the image is packed, unpack it and save it to the raw texture folder.>
        if texture_node.image.packed_file:
            bau.save_image(
                texture_node.image,
                file_format='PNG',
                image_category='RAW_TEXTURE',
                colorspace='sRGB'
            )

        # Save the image if it needs saving.
        elif texture_node.image.is_dirty:
            texture_node.image.save()
        
        # Abort the operation if the image still has no data loaded into blend memory.
        if not texture_node.image.has_data:
            return {'CANCELLED'}

        # Select and then export the image to the external image editing software.
        bau.set_texture_paint_image(texture_node.image)
        bpy.ops.image.external_edit(filepath=texture_node.image.filepath)

        return {'FINISHED'}

class RYMAT_OT_image_edit_uvs(Operator):
    bl_idname = "rymat.image_edit_uvs"
    bl_label = "Image Edit UVs"
    bl_description = "Exports the selected object's UV layout to the image editor defined in Blender's preferences (Edit -> Preferences -> File Paths -> Applications -> Image Editor)"

    def execute(self, context):
        bau.set_valid_material_editing_mode()
        bau.verify_material_operation_context(self)

        original_mode = bpy.context.object.mode
        active_object = bpy.context.active_object

        if active_object.data.uv_layers.active == None:
            self.report({'ERROR'}, "Active object has no active UV layout to export UVs for. Add one, or select a different object.")
            return{'FINISHED'}

        # Set edit mode and select all uvs.
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')

        # If the object has an active material, use that to select the UVs to export.
        if active_object.active_material:
            bpy.ops.object.material_slot_select()
            uv_image_name = active_object.active_material.name + "_UVs"

        # If there is no active material slot, select the whole mesh.
        else:
            bpy.ops.uv.select_all(action='SELECT')
            uv_image_name = bpy.context.active_object.name + "_UVs"

        # Save UV layout to the raw texture folder.
        uv_image_name = bpy.context.active_object.name + "_" + "UVLayout"
        uv_layout_path = bau.get_raw_texture_file_path(uv_image_name, 'PNG')
        bpy.ops.uv.export_layout(filepath=uv_layout_path, size=(tss.get_texture_width(), tss.get_texture_height()))

        # Load the UV layout into Blender's data so it can be exported directly from Blender.
        uv_image = bpy.data.images.get(uv_image_name + ".png")
        if uv_image:
            bpy.data.images.remove(uv_image)
        uv_layout_image = bpy.data.images.load(uv_layout_path)

        # Select and export UV layout.
        context.scene.tool_settings.image_paint.canvas = uv_layout_image
        bpy.ops.image.external_edit(filepath=uv_layout_image.filepath)

        # Reset mode.
        bpy.ops.object.mode_set(mode = original_mode)
        
        return{'FINISHED'}

class RYMAT_OT_reload_texture_node_image(Operator):
    bl_idname = "rymat.reload_texture_node_image"
    bl_label = "Reload Texture Node Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Reloads the texture node image from it's associated saved file"

    node_tree_name: StringProperty(default="", options={'HIDDEN'})
    node_name: StringProperty(default="", options={'HIDDEN'})

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        # Select and then reload the image in the texture node.
        if texture_node.image:
            context.scene.tool_settings.image_paint.canvas = texture_node.image
            bpy.ops.image.reload()
            debug_logging.log_status("Reloaded {0}.".format(texture_node.image.name), self, type='INFO')
        return {'FINISHED'}

class RYMAT_OT_duplicate_texture_node_image(Operator):
    bl_idname = "rymat.duplicate_texture_node_image"
    bl_label = "Duplicate Texture Node Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Duplicated the texture image stored in the texture node from Blender's data"

    node_tree_name: StringProperty(default="", options={'HIDDEN'})
    node_name: StringProperty(default="", options={'HIDDEN'})

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if texture_node.image:
            duplicated_image = texture_node.image.copy()
            duplicated_image.name = texture_node.image.name + "_Copy"
            texture_node.image = duplicated_image
            bau.set_texture_paint_image(duplicated_image)
            
        return {'FINISHED'}

class RYMAT_OT_delete_texture_node_image(Operator):
    bl_idname = "rymat.delete_texture_node_image"
    bl_label = "Delete Texture Node Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the texture image stored in the texture node from Blender's data, and it's saved file on disk if one exists"

    node_tree_name: StringProperty(default="", options={'HIDDEN'})
    node_name: StringProperty(default="", options={'HIDDEN'})

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_tree_name)
        if not node_group:
            debug_logging.log_status("Provided node group does not exist in Blenders data when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}

        if self.node_name == "":
            debug_logging.log_status("Provided texture node name is blank when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        texture_node = node_group.nodes.get(self.node_name)
        if not texture_node:
            debug_logging.log_status("Can't find the specified texture node when attempting to import a texture to a texture node.", self)
            return {'FINISHED'}
        
        # Delete the image in the texture node from the blend data if one exists.
        if texture_node.image:
            image_name = texture_node.image.name
            bpy.data.images.remove(texture_node.image)
            debug_logging.log_status("Deleted " + image_name, self, type='INFO')
        else:
            debug_logging.log_status("No image to delete.", self, type='INFO')

        return {'FINISHED'}
