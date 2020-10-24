# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )

from ..Operator import Isolate

# class Custom_Properties(PropertyGroup):



#     vertexNormal_floatVector: FloatVectorProperty(

#         name = "Float Value",
#         description = "VertexNormalVector",
#         subtype = 'XYZ',
#         precision=4,
#         # size=3,
#         default=(0.0000, 0.0000, 0.0000), 
#         min= 0.0000, # float
#         max = 1.0000,
#         get= get_vector,
#         set= set_vector,
        
#         )


    
# def get_vector(self):
#     return self["VectorN"]


# def set_vector(self, value):
#     self["VectorN"] = value


 
class MAIN_PT_Stitches_Edit(bpy.types.Panel):
    
    bl_label = 'Edit_Module'
    bl_idname = 'Edit_Module'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stitches'        #MainPanel
    bl_context = "mesh_edit"

    def draw(self,context):
        layout = self.layout        #Draw


class Edit_PT_SmartDelete(bpy.types.Panel):

    bl_label = 'SmartDelete'
    bl_idname = 'Edit.SmartDelete'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stitches'       
    bl_parent_id = 'Edit_Module' 
    # bl_order = 2
    # bl_options = {'DEFAULT_CLOSED'} 

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        if bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[0]:
            row.operator('edit.deleteverts')
        elif bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[1]:
            row.operator('edit.deleteedges')
        elif bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[2]:
            row.operator('edit.deletefaces')

        # row = layout.row()

        if bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[0]:
            row.operator('edit.dissolveverts')
        elif bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[1]:
            row.operator('edit.dissolveedges')
        elif bpy.context.active_object.mode == 'EDIT' and bpy.context.tool_settings.mesh_select_mode[2]:
            row.operator('edit.dissolvefaces')
        

class Edit_PT_VertexNormal(bpy.types.Panel):        #Edit Normal

    bl_label = 'VertexNormal'
    bl_idname = 'Edit.VertexNormal'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stitches'       
    bl_parent_id = 'Edit_Module' 
    # bl_options = {'DEFAULT_CLOSED'} 
    # bl_order = 1
    



    def draw(self,context):
        layout = self.layout
        row = layout.row()
        overlay = bpy.context.space_data.overlay
        row.prop(overlay, 'show_split_normals', text = '', icon = 'NORMALS_VERTEX_FACE')
        row.prop(overlay, 'normals_length', text = 'Size')

        row = layout.row()

        # print(bpy.context.scene.FloatNorVec[0])


        

        # Get_Vec = bpy.context.scene.tool_settings.normal_vector

        
        # print(Get_Vec)
        # bpy.context.scene.FloatNorVec[0] = Get_Vec[0]
        # bpy.context.scene.FloatNorVec[1] = Get_Vec[1]
        # bpy.context.scene.FloatNorVec[2] = Get_Vec[2]

        




        # bpy.types.ToolSettings.normal_vector[0] = bpy.context.scene.FloatNorVec[0]
        # bpy.types.ToolSettings.normal_vector[1] = bpy.context.scene.FloatNorVec[1]
        # bpy.types.ToolSettings.normal_vector[2] = bpy.context.scene.FloatNorVec[2]

        # bpy.types.ToolSettings.normal_vector[0] = Set_Vec[0]
        # bpy.types.ToolSettings.normal_vector[1] = Set_Vec[1]
        # bpy.types.ToolSettings.normal_vector[2] = Set_Vec[2]



        # print(Get_Vec)

        if bpy.context.tool_settings.mesh_select_mode[1] ==False:

            row.prop(bpy.context.scene,'FloatNorVec',text='')
            row = layout.row()
            row.operator('edit.getvernor')

            row.operator('edit.setvernor')

            normal_reset = row.operator('mesh.normals_tools',text='Reset')
            normal_reset.mode='RESET'
            normal_reset.absolute=False

        # bpy.context.area.tag_redraw()

class Edit_OT_BothSeamSharp(bpy.types.Operator):
    bl_label = 'Both'
    bl_idname = 'edit.bothseamsharp'

    def execute(self,context):
        bpy.ops.mesh.mark_seam()
        bpy.ops.mesh.mark_sharp()
        return {'FINISHED'}

class Edit_OT_ClearSeamSharp(bpy.types.Operator):
    bl_label = 'Clear'
    bl_idname = 'edit.clearseamsharp'

    def execute(self,context):
        bpy.ops.mesh.mark_seam(clear=True)
        bpy.ops.mesh.mark_sharp(clear=True)
        return {'FINISHED'}

        


class Edit_PT_editPanel(bpy.types.Panel):        #Edit Panel

    bl_label = 'Edit'
    bl_idname = 'Edit.editpanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stitches'       
    bl_parent_id = 'Edit_Module' 
    # bl_options = {'DEFAULT_CLOSED'} 
    # bl_order = 3

    


    def draw(self,context):
        layout = self.layout
        # row = layout.row()

        box = layout.box()
        row = box.row()
        seam_m = row.operator('mesh.mark_seam')
        # seam_m.clear=False
        seam_c = row.operator('mesh.mark_seam',text='Clear Seam')
        seam_c.clear=True
        row = box.row()
        sharp_m = row.operator('mesh.mark_sharp')
        sharp_c = row.operator('mesh.mark_sharp',text='Clear Sharp')
        sharp_c.clear=True
        row = box.row()
        row.operator('edit.bothseamsharp')
        row.operator('edit.clearseamsharp')

        box = layout.box()
        row = box.row()
        row.operator('mesh.flatten')
        row.operator('mesh.circle')
        row = box.row()
        # bpy.ops.mesh.remove_doubles(threshold=0.001)
        mergeVertex = row.operator('mesh.remove_doubles',text='Merge By Distance')
        mergeVertex.threshold=0.01
        # bpy.ops.mesh.merge(type='CENTER')
        mergeVertexC = row.operator('mesh.merge',text='Merge At Center')
        mergeVertexC.type='CENTER'

        row = box.row()
        Collapse = row.operator('mesh.merge',text='Collapse')
        Collapse.type='COLLAPSE'

        row.operator('mesh.edgeflow',text='Set Edge Flow')
        # row.operator('mesh.edgelinear',text='Set Edge Linear')

        row = box.row()
        separate = row.operator('mesh.separate')
        separate.type = 'SELECTED'
        row = box.row()
        
        if Isolate.bool_v == 0:
            row.operator('edit.isolate')
        else:
            row.operator('edit.isolateoff')

       
        






#------------------Register&Unregister------------------

classes = [


    # Custom_Properties,

    MAIN_PT_Stitches_Edit,
    Edit_PT_VertexNormal,
    Edit_PT_SmartDelete,
    Edit_OT_BothSeamSharp,
    Edit_OT_ClearSeamSharp,
    Edit_PT_editPanel,
    
]


def register():
    
    Isolate.register()
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # bpy.types.Scene.FloatNorVec = bpy.props.FloatVectorProperty(get=get_vector, set=set_vector,precision=5,min=0.0,max=1.0)

    # bpy.types.Scene.FloatNorVec = PointerProperty(type=Custom_Properties)

def unregister():   
    
    Isolate.unregister()
    for cls in classes:
        bpy.utils.unregister_class(cls)


    