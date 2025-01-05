import bpy
from ..core import blender_addon_utils as bau

def draw_render_device_settings(layout):
    '''Draws render device settings crucial for improving baking speeds.'''

    row = layout.row()
    row.separator()

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
    if scene.cycles.device == 'CPU':
        row.label(text="", icon='ERROR')
    row.prop(bpy.data.scenes["Scene"].cycles, "device", text="")

    # Draw the (Cycles) render device type.
    row = first_column.row()
    row.label(text="Render Device Type")
    row = second_column.row()
    compute_device_preference = bpy.context.preferences.addons['cycles'].preferences
    if compute_device_preference.compute_device_type == 'NONE':
        row.label(text="", icon='ERROR')
    row.prop(compute_device_preference, "compute_device_type", text="")

    split = layout.split(factor=0.05)
    first_column = split.column()
    second_column = split.column()
    
    # Draw a warning for users using their CPU to export textures.
    scene = bpy.data.scenes["Scene"]
    if scene.cycles.device == 'CPU':
        row = first_column.row()
        row.label(text="", icon='ERROR')
        row = second_column.row()
        row.label(text="Exporting is slow with your CPU!")

    # Draw a warning for users not using a Cycles render device.
    cycles_render_device = bpy.context.preferences.addons['cycles'].preferences.compute_device_type
    if cycles_render_device == 'NONE':
        row = first_column.row()
        row.label(text="", icon='ERROR')
        row = second_column.row()
        row.label(text="Exporting is slow without a defined render device type!")
    
    # Draw a separator to visually distiguish this section from other settings.
    layout.separator(type='LINE')