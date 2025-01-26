import bpy
from ..core import blender_addon_utils as bau
from . import bpy_ui_wrappers as bui

def draw_render_device_settings(layout):
    '''Draws render device settings crucial for improving baking speeds.'''

    row = layout.row()
    bui.separator(row, type='NONE')

    row = layout.row()
    row.label(text="RENDER DEVICES")

    # Use a two column layout.
    split = layout.split(factor=0.4)
    first_column = split.column()
    second_column = split.column()

    # Draw the render device.
    row = first_column.row()
    row.label(text="Render Device")
    row = second_column.row()
    scene = bpy.data.scenes["Scene"]
    row.prop(bpy.data.scenes["Scene"].cycles, "device", text="")

    # Draw the (Cycles) render device type.
    row = first_column.row()
    row.label(text="Render Device Type")
    row = second_column.row()
    compute_device_preference = bpy.context.preferences.addons['cycles'].preferences
    row.prop(compute_device_preference, "compute_device_type", text="")
    
    # Draw a warning for users using their CPU to export textures.
    scene = bpy.data.scenes["Scene"]
    if scene.cycles.device == 'CPU':
        bau.print_aligned_text(
            layout,
            aligned_text="Baking is slow with your CPU!",
            alignment='CENTER',
            label_icon='ERROR'
        )

    # Draw a warning for users not using a Cycles render device.
    cycles_render_device = bpy.context.preferences.addons['cycles'].preferences.compute_device_type
    if cycles_render_device == 'NONE':
        bau.print_aligned_text(
            layout,
            aligned_text="Baking is slow without a defined render device type!",
            alignment='CENTER',
            label_icon='ERROR'
        )
    
    # Draw a separator to visually distiguish this section from other settings.
    bui.separator(layout, type='LINE')