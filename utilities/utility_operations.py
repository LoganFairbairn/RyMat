# This module contains extra utility operations that assist with using this add-on or material editing in general.

import bpy
import os
from bpy.types import Operator
from bpy.utils import resource_path
from ..core import material_channels
from ..core import layer_nodes
from ..core import layer_masks
from ..utilities import logging
from pathlib import Path
from ..preferences import ADDON_NAME

class MATLAYER_OT_set_decal_layer_snapping(Operator):
    bl_idname = "matlayer.set_decal_layer_snapping"
    bl_label = "Set Decal Layer Snapping"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Sets optimal snapping settings for positioning decal layers. You can disable the snapping mode by selecting the magnet icon in the middle top area of the 3D viewport"

    def execute(self, context):
        bpy.context.scene.tool_settings.use_snap = True
        bpy.context.scene.tool_settings.snap_elements = {'FACE'}
        bpy.context.scene.tool_settings.snap_target = 'CENTER'
        bpy.context.scene.tool_settings.use_snap_align_rotation = True
        return {'FINISHED'}

class MATLAYER_OT_append_workspace(Operator):
    bl_idname = "matlayer.append_workspace"
    bl_label = "Append Workspace"
    bl_description = "Appends a suggested workspace for using this add-on"

    def execute(self, context):
        workspace = bpy.data.workspaces.get('Matlayer')
        if workspace:
            logging.popup_message_box("The default workspace already exists, manually delete it and click this operator again to re-load the workspace.", 'Info', 'INFO')
            return {'FINISHED'}
        
        previously_selected_object = bpy.context.active_object

        USER = Path(resource_path('USER'))
        ADDON = ADDON_NAME
        BLEND_FILE = "Matlayer.blend"
        source_path =  str(USER / "scripts/addons" / ADDON / "blend" / BLEND_FILE)
        
        with bpy.data.libraries.load(source_path) as (data_from, data_to):
            data_to.workspaces = ["Matlayer"]

        # Set the current workspace to the appended workspace.
        bpy.context.window.workspace = bpy.data.workspaces['Matlayer']

        # Reset the main pannel tab.
        context.scene.matlayer_panel_properties.sections = 'SECTION_TEXTURE_SET'
        
        # Frame selected objects.
        '''
        bpy.ops.object.select_all(action='DESELECT')
        previously_selected_object.select_set(True)
        bpy.context.view_layer.objects.active = previously_selected_object
        bpy.ops.view3d.view_selected(use_all_regions=True)
        '''

        # Set up a material asset browser for the user.
        preferences = bpy.context.preferences
        if not preferences.filepaths.asset_libraries.get("MatLayer Default Assets"):
            bpy.ops.preferences.asset_library_add()
            new_library = bpy.context.preferences.filepaths.asset_libraries[-1]
            new_library.name = "MatLayer Default Assets"
            new_library.path = str(USER / "scripts/addons" / ADDON / "blend")

        self.report({'INFO'}, "Appended workspace (check the workspaces / user interface layouts at the top of your screen).")

        return {'FINISHED'}

class MATLAYER_OT_append_basic_brushes(Operator):
    bl_idname = "matlayer.append_basic_brushes"
    bl_label = "Append Basic Brushes"
    bl_description = "Appends basic brush presets to the current blend file"

    def execute(self, context):
        brush_prefix = "ML_"

        # Delete any Matlayer brushes if they exist before re-importing them.
        for brush in bpy.data.brushes:
            if brush.name.startswith(brush_prefix):
                bpy.data.brushes.remove(brush)

        USER = Path(resource_path('USER'))
        BLEND_FILE = "Matlayer.blend"
        source_path =  str(USER / "scripts/addons" / ADDON_NAME / "blend" / BLEND_FILE)

        with bpy.data.libraries.load(source_path) as (data_from, data_to):
            data_to.brushes = [name for name in data_from.brushes if name.startswith(brush_prefix)]
            
        # For all loaded brushes, assign a brush icon image.
        brush_preview_images_path = str(USER / "scripts/addons" / ADDON_NAME / "brush_icons")
        for brush in bpy.data.brushes:
            if brush.name.startswith(brush_prefix):
                brush.use_custom_icon = True
                brush_icon_name = brush.name.split('_')[1]
                brush.icon_filepath = os.path.join(brush_preview_images_path, brush_icon_name + ".png")

        self.report({'INFO'}, "Appended basic brushes. Check the brush presets to see them (Texture Paint Mode -> Tool (3D view sidebar) -> Brushes)")

        return {'FINISHED'}

class MATLAYER_OT_delete_unused_external_images(Operator):
    bl_idname = "matlayer.delete_unused_external_images"
    bl_label = "Delete Unused External Images"
    bl_description = "Deletes unused saved layer and mask images from folders. This is a quick method for clearing out unused textures created with this add-on"

    def execute(self, context):
        used_image_paths = []

        material_layers = context.scene.matlayer_layers
        masks = context.scene.matlayer_masks
        material_channel_list = material_channels.get_material_channel_list()

        for material_channel_name in material_channel_list:
            for i in range(0, len(material_layers)):
                nodes = layer_nodes.get_all_nodes_in_layer(material_channel_name, i, context, False)
                for node in nodes:
                    if node:
                        if node.bl_static_type == 'TEX_IMAGE':
                            if node.image != None and node.image.filepath != '':
                                if node.image.filepath not in used_image_paths:
                                    used_image_paths.append(node.image.filepath)
                                    print("Added image path: " + node.image.filepath)

        for i in range(0, len(material_layers)):
            for c in range(0, len(masks)):
                node = layer_masks.get_mask_node('MASK-TEXTURE', material_channel_name, i, c, False)
                if node:
                    if node.bl_static_type == 'TEX_IMAGE':
                        if node.image != None and node.image.filepath != '':
                            if node.image.filepath not in used_image_paths:
                                used_image_paths.append(node.image.filepath)
                                print("Added image path: " + node.image.filepath)


        # Delete all images in the layer / mask folder that are not linked to any layers.
        matlayer_image_path = os.path.join(bpy.path.abspath("//"), "Matlayer")
        layer_image_path = os.path.join(matlayer_image_path, "Layers")
        mask_image_path = os.path.join(matlayer_image_path, "Masks")

        folder_images = []
        if os.path.exists(layer_image_path):
            for file in os.listdir(layer_image_path):
                file_path = os.path.join(layer_image_path, file)
                folder_images.append(file_path)
                print("Added file: " + file_path)

        if os.path.exists(mask_image_path):
            for file in os.listdir(mask_image_path):
                file_path = os.path.join(mask_image_path, file)
                folder_images.append(file_path)
                print("Added file: " + file_path)
        
        deleted_unused_images = False
        for path in folder_images:
            if path not in used_image_paths:
                if os.path.exists(path):
                    os.remove(path)
                    print("Deleted unused image: " + path)
                    deleted_unused_images = True

        if deleted_unused_images:
            self.report({'INFO'}, "Deleted unused images. See terminal for list (on Windows: Window -> Toggle System Console)")
        else:
            self.report({'INFO'}, "No unused images to delete.")

        return{'FINISHED'}