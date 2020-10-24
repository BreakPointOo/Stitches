import bpy


bool_v = 0
Var1 = 0

class Edit_OT_Isolate(bpy.types.Operator):
    bl_label = 'Isolate'
    bl_idname = 'edit.isolate'

    
    def execute(self,context):
        global Var1
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces[0]
                if space.local_view : #check if using local view
                    Var1 = 1
                else:
                    Var1 = 0
                    bpy.ops.view3d.localview(frame_selected=False)
        
        # bpy.ops.object.hide_view_set(unselected=True)
        bpy.ops.mesh.hide(unselected=True)
        global bool_v

        bool_v = 1

        return {'FINISHED'}


class Edit_OT_IsolateOff(bpy.types.Operator):
    bl_label = 'OFF'
    bl_idname = 'edit.isolateoff'

    def execute(self,context):
        global Var1

        if Var1 == 0:
            bpy.ops.view3d.localview(frame_selected=False)

        bpy.ops.mesh.reveal(select=False)

        global bool_v

        bool_v = 0
        # bpy.ops.mesh.select_all(action='DESELECT')
        # bpy.ops.object.hide_view_clear(select=False)

        return {'FINISHED'}

classes = [

    Edit_OT_Isolate,
    Edit_OT_IsolateOff,

]


def register():
    
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():   
    
     for cls in classes:
        bpy.utils.unregister_class(cls)

