bl_info = {
    "name": "Stitches",
    "description": "Stitches",
    "author": "○",
    "version": (0, 5, 12),
    "blender": (2, 83, 0),
    "location": "View3D",
    "wiki_url": "https://github.com/BreakPointOo/Stitches",
    "category": "3D View"}


import re
import os
from imp import reload

if "bpy" in locals():


    reload(Edit_Module)
    reload(Object_Module)
    reload(UV_Module)
    reload(pivot)
    reload(SmartDelete)
    reload(VertexNormal)
    reload(RenameObjects)
    reload(Flatten)
    reload(edge_flow)
    reload(AlignUV)

else:

    import bpy
    from .Modules import Edit_Module
    from .Modules import Object_Module
    from .Modules import UV_Module
    from .Operator import pivot
    from .Operator import SmartDelete
    # from .Operator.UVIsland_HardEdges import *
    from .Operator import VertexNormal
    from .Operator import RenameObjects
    from .Operator import Flatten
    from .Operator import edge_flow
    from .Operator import AlignUV


#------------------Register&Unregister------------------



def register():
    
    Object_Module.register()
    pivot.register()
    SmartDelete.register()
    Edit_Module.register()
    VertexNormal.register()
    RenameObjects.register()
    Flatten.register()
    edge_flow.register()
    UV_Module.register()
    AlignUV.register()



def unregister():   
    
    Object_Module.unregister()
    pivot.unregister()
    SmartDelete.unregister()
    Edit_Module.unregister()
    VertexNormal.unregister()
    RenameObjects.unregister()
    Flatten.unregister()
    edge_flow.unregister()
    UV_Module.unregister()
    AlignUV.unregister()


