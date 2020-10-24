import bpy

class Obj_OT_DeleteObj(bpy.types.Operator):     #delete object
    bl_label = 'DelObj'
    bl_idname = 'obj.deleteobj'

    def execute(self,context):

        if bpy.context.active_object.mode != 'EDIT':
            bpy.ops.object.delete()
        
        return{'FINISHED'}


class Edit_OT_DeleteVerts(bpy.types.Operator):      #delete verts
    bl_label = 'DelVerts'
    bl_idname = 'edit.deleteverts'

    def execute(self,context):

        if bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[0]:
            bpy.ops.mesh.delete(type= 'VERT')
    
        return{'FINISHED'}


class Edit_OT_DeleteEdges(bpy.types.Operator):      #delete edges
    bl_label = 'DelEdges'
    bl_idname = 'edit.deleteedges'

    def execute(self,context):

        if bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[1]:
            bpy.ops.mesh.delete(type= 'EDGE')
    
        return{'FINISHED'}


class Edit_OT_DeleteFaces(bpy.types.Operator):      #delete faces
    bl_label = 'DelFaces'
    bl_idname = 'edit.deletefaces'

    def execute(self,context):

        if bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[2]:
            bpy.ops.mesh.delete(type= 'FACE')
    
        return{'FINISHED'}






class Edit_OT_DissolveVerts(bpy.types.Operator):      #dissolve verts
    bl_label = 'DissolveVerts'
    bl_idname = 'edit.dissolveverts'

    def execute(self,context):

        if bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[0]:
            bpy.ops.mesh.dissolve_verts()
    
        return{'FINISHED'}


class Edit_OT_DissolveEdges(bpy.types.Operator):        #dissolve edges
    bl_label = 'DissolveEdges'
    bl_idname = 'edit.dissolveedges'

    def execute(self,context):

        if bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[1]:
            bpy.ops.mesh.dissolve_edges()
    
        return{'FINISHED'}


class Edit_OT_DissolveFaces(bpy.types.Operator):        #dissolve faces
    bl_label = 'DissolveFaces'
    bl_idname = 'edit.dissolvefaces'

    def execute(self,context):

        if bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[2]:
            bpy.ops.mesh.dissolve_faces()
    
        return{'FINISHED'}

    
Classes = [

    Obj_OT_DeleteObj,
    Edit_OT_DeleteVerts,
    Edit_OT_DeleteEdges,
    Edit_OT_DeleteFaces,
    Edit_OT_DissolveVerts,
    Edit_OT_DissolveEdges,
    Edit_OT_DissolveFaces,

]

def register():

    for cls in Classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in Classes:
        bpy.utils.unregister_class(cls)