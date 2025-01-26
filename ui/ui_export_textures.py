# This files handles drawing the exporting section's user interface.

import bpy
from bpy.types import Menu
from ..core import material_layers
from ..core import blender_addon_utils as bau
from . import bpy_ui_wrappers as bui
from . import ui_render_devices

def verify_exporting_textures_is_valid(context):
    '''Runs checks to verify if exporting textures is possible. If exporting textures is invalid, an info message will be returned.'''
    if not context.active_object:
        return "No Active Object"
    
    if context.active_object.active_material == None:
        return "No Active Material"
    
    if bau.verify_addon_material(context.active_object.active_material) == False:
        return "Material Invalid"

    return ""

def draw_export_textures_ui(self, context):
    '''Draws user interface for the export section.'''
    layout = self.layout

    # Display a message when there is no active object.
    exporting_textures_error = verify_exporting_textures_is_valid(context)
    if exporting_textures_error != "":
        bau.print_aligned_text(layout, "Can't Export Textures", alignment='CENTER')
        bau.print_aligned_text(layout, exporting_textures_error, alignment='CENTER')
        return

    # Draw export button.
    row = layout.row(align=True)
    row.scale_y = 2.0
    row.operator("rymat.export", text="Export Textures")

    # Draw render device settings.
    ui_render_devices.draw_render_device_settings(layout)

    # Draw options for changing the export preset.
    row = layout.row(align=True)
    texture_export_settings = bpy.context.scene.rymat_texture_export_settings
    row.menu("RYMAT_MT_export_preset_menu", text="Select Preset")
    row.operator("rymat.save_export_template", text="", icon='FILE_TICK')
    row.operator("rymat.refresh_export_template_list", text="", icon='FILE_REFRESH')
    row.operator("rymat.delete_export_template", text="", icon='TRASH')

    # Split the UI into a two column layout.
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()
    
    # Draw the name of the active export preset.
    texture_export_settings = bpy.context.scene.rymat_texture_export_settings
    row = first_column.row()
    row.label(text="Export Preset Name")
    row = second_column.row()
    row.prop(texture_export_settings, "export_preset_name", text="")

    # Draw the export folder.
    baking_settings = bpy.context.scene.rymat_baking_settings
    row = first_column.row()
    row.label(text="Export Folder")
    row = second_column.row(align=True)
    row.prop(bpy.context.scene, "rymat_export_folder", text="")
    row.operator("rymat.set_export_folder", text="", icon='FOLDER_REDIRECT')
    row.operator("rymat.open_export_folder", text="", icon='FILE_FOLDER')

    # Draw the export mode.
    row = first_column.row()
    row.label(text="Export Mode")
    row = second_column.row()
    row.prop(texture_export_settings, "export_mode", text="")
    
    row = first_column.row()
    row.label(text="Normal Map Mode")
    row = second_column.row(align=True)
    row.prop_enum(texture_export_settings, "normal_map_mode", 'OPEN_GL')
    row.prop_enum(texture_export_settings, "normal_map_mode", 'DIRECTX')

    row = first_column.row()
    row.label(text="Roughness Mode")
    row = second_column.row(align=True)
    row.prop_enum(texture_export_settings, "roughness_mode", 'ROUGHNESS')
    row.prop_enum(texture_export_settings, "roughness_mode", 'SMOOTHNESS')

    row = first_column.row()
    row.label(text="UV Padding")
    row = second_column.row()
    row.prop(baking_settings, "uv_padding", text="")

    row = first_column.row()
    row.label(text="Samples")
    row = second_column.row()
    row.prop(texture_export_settings, "samples", text="")
    
    active_object = bpy.context.active_object
    if active_object:
        export_uv_map_node = material_layers.get_material_layer_node('EXPORT_UV_MAP')
        if export_uv_map_node:
            row = first_column.row()
            row.label(text="Export UV Map")
            row = second_column.row()
            row.prop_search(export_uv_map_node, "uv_map", active_object.data, "uv_layers", text="")

    # Draw export textures and their settings.
    row = first_column.row()
    row.scale_y = 1.5
    row.label(text="EXPORT TEXTURES")
    row = second_column.row(align=True)
    row.scale_x = 1.5
    row.scale_y = 1.5
    row.alignment = 'RIGHT'
    row.operator("rymat.add_export_texture", text="", icon='ADD')

    # Draw channel packing textures.
    for i, texture in enumerate(texture_export_settings.export_textures):
        row = layout.row()
        bui.separator(layout, type='LINE')
        split = layout.split(factor=0.4)
        first_column = split.column()
        second_column = split.column()

        row = first_column.row()
        row.label(text=str(i + 1) + ".")
        row = second_column.row()
        row.prop(texture, "name_format", text="")
        op = row.operator("rymat.remove_export_texture", icon='X', text="")
        op.export_texture_index = i

        row = first_column.row()
        row.label(text="Image Settings")
        row = second_column.row(align=True)
        row.prop(texture, "image_format", text="")
        row.prop(texture, "colorspace", text="")
        row.prop(texture, "bit_depth", text="")

        row = first_column.row()
        row.label(text="Red Packing")
        split = second_column.split(factor=0.5)
        sub_column_1 = split.column()
        sub_column_2 = split.column()
        row = sub_column_1.row()
        row.prop(texture.pack_textures, "r_texture", text="")
        row = sub_column_2.row()
        row.alignment = 'CENTER'
        row.prop(texture.input_rgba_channels, "r_color_channel", text="")
        row.label(text="->")
        row.prop(texture.output_rgba_channels, "r_color_channel", text="")

        row = first_column.row()
        row.label(text="Green Packing")
        split = second_column.split(factor=0.5)
        sub_column_1 = split.column()
        sub_column_2 = split.column()
        row = sub_column_1.row()
        row.prop(texture.pack_textures, "g_texture", text="")
        row = sub_column_2.row()
        row.alignment = 'CENTER'
        row.prop(texture.input_rgba_channels, "g_color_channel", text="")
        row.label(text="->")
        row.prop(texture.output_rgba_channels, "g_color_channel", text="")

        row = first_column.row()
        row.label(text="Blue Packing")
        split = second_column.split(factor=0.5)
        sub_column_1 = split.column()
        sub_column_2 = split.column()
        row = sub_column_1.row()
        row.prop(texture.pack_textures, "b_texture", text="")
        row = sub_column_2.row()
        row.alignment = 'CENTER'
        row.prop(texture.input_rgba_channels, "b_color_channel", text="")
        row.label(text="->")
        row.prop(texture.output_rgba_channels, "b_color_channel", text="")

        row = first_column.row()
        row.label(text="Alpha Packing")
        split = second_column.split(factor=0.5)
        sub_column_1 = split.column()
        sub_column_2 = split.column()
        row = sub_column_1.row()
        row.prop(texture.pack_textures, "a_texture", text="")
        row = sub_column_2.row()
        row.alignment = 'CENTER'
        row.prop(texture.input_rgba_channels, "a_color_channel", text="")
        row.label(text="->")
        row.prop(texture.output_rgba_channels, "a_color_channel", text="")