# This file provides functions to assist with importing and editing with image files made with this add-on.

import bpy
from bpy.types import Operator
import random
import os       # For saving layer images.
from ..import layer_nodes

def get_image_name(layer_name):
    '''Returns the image name'''
    bpy.context.scene.coater_layers
    layer_index = bpy.context.scene.coater_layer_stack.layer_index

def save_layer_image(image_name):
    '''Saves the given layer image to the designated layer folder.'''
    print("")

def rename_layer_image(image_name, new_name):
    '''Renames the given layer image to the new name.'''
    print("")

def get_random_image_id():
    '''Generates a random image id number.'''
    return str(random.randrange(10000,99999))

class COATER_OT_add_layer_image(Operator):
    '''Creates a image and adds it to the selected image layer'''
    bl_idname = "coater.add_layer_image"
    bl_label = "Add Layer Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Creates a image and adds it to the selected image layer"

    # Specified material channel.
    material_channel: bpy.props.StringProperty()

    def execute(self, context):
        layers = context.scene.coater_layers
        layer_index = context.scene.coater_layer_stack.layer_index

        # Assign the new image the layer name + a random image id number.
        layer_name = layers[layer_index].name.replace(" ", "")
        image_name = layer_name + "_" + get_random_image_id()

        while bpy.data.images.get(image_name) != None:
            image_name = layer_name + "_" + get_random_image_id()

        # Create a new image of the texture size defined in the texture set settings.
        texture_set_settings = context.scene.coater_texture_set_settings
        image_width = 128
        if texture_set_settings.image_width == 'FIVE_TWELVE':
            image_width = 512
        if texture_set_settings.image_width == 'ONEK':
            image_width = 1024
        if texture_set_settings.image_width == 'TWOK':
            image_width = 2048
        if texture_set_settings.image_width == 'FOURK':
            image_width = 4096

        image_height = 128
        if texture_set_settings.image_height == 'FIVE_TWELVE':
            image_height = 512
        if texture_set_settings.image_height == 'ONEK':
            image_height = 1024
        if texture_set_settings.image_height == 'TWOK':
            image_height = 2048
        if texture_set_settings.image_height == 'FOURK':
            image_height = 4096

        image = bpy.ops.image.new(name=image_name,
                                  width=image_width,
                                  height=image_height,
                                  color=(0.0, 0.0, 0.0, 0.0),
                                  alpha=True,
                                  generated_type='BLANK',
                                  float=False,
                                  use_stereo_3d=False,
                                  tiled=False)

        # Save the images to a folder (unless they are being packed into the blend file).
        if texture_set_settings.pack_images == False:
            layers_folder_path = bpy.path.abspath("//") + 'Layer Images'

            if os.path.exists(layers_folder_path) == False:
                os.mkdir(layers_folder_path)

            layer_image = bpy.data.images[image_name]
            layer_image.filepath = layers_folder_path + "/" + image_name + ".png"
            layer_image.file_format = 'PNG'

            layer_image.pixels[0] = 1

            if layer_image != None:
                if layer_image.is_dirty:
                    layer_image.save()


        # Add the new image to the selected layer.
        selected_layer_index = context.scene.coater_layer_stack.layer_index
        texture_node = layer_nodes.get_layer_node("TEXTURE", self.material_channel, selected_layer_index, context)
        if texture_node:
            texture_node.image = bpy.data.images[image_name]
        
        return {'FINISHED'}

class COATER_OT_delete_layer_image(Operator):
    '''Deletes the current layer image from Blender's data'''
    bl_idname = "coater.delete_layer_image"
    bl_label = "Delete Layer Image"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Deletes the current layer image from Blender's data"

    # Specified material channel.
    material_channel: bpy.props.StringProperty()

    def execute(self, context):
        selected_layer_index = context.scene.coater_layer_stack.layer_index
        texture_node = layer_nodes.get_layer_node("TEXTURE", self.material_channel, selected_layer_index, context)

        if texture_node.image:
            bpy.data.images.remove(texture_node.image )
        
        return {'FINISHED'}