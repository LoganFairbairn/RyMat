# This file contains properties for the layer stack.

import bpy
from bpy.types import PropertyGroup
from . import material_channels
from ..core import layer_nodes
from ..core import layer_masks
from . import material_filters

# List of all material channel names available in this add-on.
MATERIAL_CHANNEL_NAMES = ("COLOR", "METALLIC", "ROUGHNESS", "NORMAL", "HEIGHT", "EMISSION", "SCATTERING")

def update_selected_material_channel(self, context):
    '''Updates values when the selected material channel is updated.'''
    layers = context.scene.matlay_layers
    selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel

    # Update the opacity and blend mode for all layers.
    for i in range(0, len(layers)):
        opacity_node = layer_nodes.get_layer_node("OPACITY", selected_material_channel, i, context)
        if opacity_node:
            layers[i].opacity = opacity_node.inputs[1].default_value

    # If the material channel preview is on, update the material channel preview.
    if context.scene.matlay_layer_stack.material_channel_preview == True:
        material_channels.isolate_material_channel(True, selected_material_channel, context)

def update_layer_index(self, context):
    '''Updates stuff when the selected layer is changed.'''
    # Select an the texture image for the selected material channel in the selected layer.
    selected_material_channel = context.scene.matlay_layer_stack.selected_material_channel
    selected_layer_index = context.scene.matlay_layer_stack.layer_index

    bpy.context.scene.tool_settings.image_paint.mode = 'IMAGE'
    texture_node = layer_nodes.get_layer_node("TEXTURE", selected_material_channel, selected_layer_index, context)

    if texture_node:
        if texture_node.bl_idname == "ShaderNodeTexImage":
            if texture_node.image:
                context.scene.tool_settings.image_paint.canvas = texture_node.image

    material_filters.refresh_material_filter_stack(context)
    layer_masks.read_masks(context)

def verify_layer_stack_index(layer_stack_index, context):
    '''Verifies the given layer stack index exists.'''
    layers = context.scene.matlay_layers
    if layer_stack_index <= len(layers) - 1 and layer_stack_index >= 0:
        return True
    else:
        return False

class MATLAY_layer_stack(PropertyGroup):
    '''Properties for the layer stack.'''
    # TODO: Rename this variable to selected_layer_index to make it more apparent this is the selected layer index.
    layer_index: bpy.props.IntProperty(default=-1, update=update_layer_index)
    material_channel_preview: bpy.props.BoolProperty(name="Material Channel Preview", description="If true, only the rgb output values for the selected material channel will be used on the object.", default=False)
    node_default_width: bpy.props.IntProperty(default=250)
    node_spacing: bpy.props.IntProperty(default=80)
    selected_material_channel: bpy.props.EnumProperty(items=material_channels.MATERIAL_CHANNELS, name="Material Channel", description="The currently selected material channel", default='COLOR', update=update_selected_material_channel)
    auto_update_layer_properties: bpy.props.BoolProperty(name="Auto Update Layer Properties", description="When true, select layer properties are automatically updated when changed. This toggle is used for rare cases when you want to perform an operation where layer properties are edited without them automatically updating (i.e refreshing / reading the layer stack)", default=True)

    # Note: These tabs exist to help keep the user interface elements on screen limited, thus simplifying the editing process, and helps avoid the need to scroll down on the user interface to see settings (which is annoying when using a tablet pen).
    # Tabs for material / mask layer properties.
    layer_property_tab: bpy.props.EnumProperty(
        items=[('MATERIAL', "MATERIAL", "Material settings for the selected layer."),
               ('MASK', "MASK", "Mask settings for the selected layer.")],
        name="Layer Properties Tab",
        description="Tabs for layer properties.",
        default='MATERIAL',
        options={'HIDDEN'},
    )

    material_property_tab: bpy.props.EnumProperty(
        items=[('MATERIAL', "MATERIAL", "Material properties for the selected material layer."),
               ('PROJECTION', "PROJECTION", "Projection settings for the selected material layer."),
               ('FILTERS', "FILTERS", "Layer filters and their properties for the selected material layer.")],
        name="Material Property Tabs",
        description="Tabs for material layer properties.",
        default='MATERIAL',
        options={'HIDDEN'},       
    )

    mask_property_tab: bpy.props.EnumProperty(
        items=[('FILTERS', "FILTERS", "Masks, their properties and filters for masks."),
               ('PROJECTION', "PROJECTION", "Projection settings for the selected mask.")],
        name="Mask Property Tabs",
        description="Tabs for layer mask properties.",
        default='FILTERS',
        options={'HIDDEN'},
    )