import bpy

def get_vector(self):
    return self["vn"]


def set_vector(self, value):
    self["vn"] = value


class Edit_OT_GetVertexNormal(bpy.types.Operator):

    bl_label = 'Get'
    bl_idname = 'edit.getvernor'

    def execute(self,context):

        bpy.ops.mesh.normals_tools(mode='COPY')

        Get_Vec = bpy.context.scene.tool_settings.normal_vector
        
        bpy.context.scene.FloatNorVec[0] = Get_Vec[0]
        bpy.context.scene.FloatNorVec[1] = Get_Vec[1]
        bpy.context.scene.FloatNorVec[2] = Get_Vec[2]

        return{'FINISHED'}

class Edit_OT_SetVertexNormal(bpy.types.Operator):

    bl_label = 'Set'
    bl_idname = 'edit.setvernor'

    def execute(self,context):  

        bpy.context.scene.tool_settings.normal_vector = bpy.context.scene.FloatNorVec
        bpy.ops.mesh.normals_tools(mode='PASTE')
        return{'FINISHED'}

classes = [

    Edit_OT_GetVertexNormal,
    Edit_OT_SetVertexNormal,

]

def register():
    bpy.types.Scene.FloatNorVec = bpy.props.FloatVectorProperty(get=get_vector, set=set_vector,precision=5,min=-1,max=1)
    for cls in classes:
        bpy.utils.register_class(cls)



def unregister():   
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

