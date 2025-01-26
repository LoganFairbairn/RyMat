# This module contains function wrappers for drawing Blender user interface while maintaining compatability with different versions of Blender.

import bpy

def separator(layout, type='LINE'):
    '''Draws a separator in the user interface.'''
    version = bpy.app.version

    # Separators can be drawn with types in Blender 4.3 and above.
    if version >= (4, 3, 0):
        layout.separator(type)
    
    else:
        layout.separator()