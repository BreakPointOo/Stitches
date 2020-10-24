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

from ..Operator.UVIsland_HardEdges import *


class MAIN_PT_Stitches_Obj(bpy.types.Panel):
    
    bl_label = 'Mesh_Module'
    bl_idname = 'Object_Module'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stitches'        #MainPanel
    bl_context = "objectmode"

    
    def draw(self,context):
        layout = self.layout        #Draw

 
class C_PT_FilePanel(bpy.types.Panel):    #Import & Export FBX

    bl_label = 'File(FBX)'
    bl_idname = 'FilePanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stitches'
    bl_parent_id = 'Object_Module' 
    bl_options = {'DEFAULT_CLOSED'} 
    # bl_order = 1

    
    def draw(self,context):

        layout = self.layout
        row = layout.row()

        ot = row.operator('import_scene.fbx')

        ot = row.operator('export_scene.fbx')
        ot.use_selection = True
        ot.bake_anim = False
        ot.add_leaf_bones = False

 
class C_PT_MCPanel(bpy.types.Panel):     #Mesh & Curve Panel
    
    
    bl_label = 'Add Mesh&Curve'
    bl_idname = 'MCPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stitches'
    bl_parent_id = 'Object_Module'  
    # bl_order = 3   

    
    def draw(self,context):
        
        layout = self.layout
        row = layout.row()
    

        row.operator('mesh.primitive_cube_add',icon='CUBE',text= 'Cube')     
        row.operator('mesh.primitive_cylinder_add',icon='MESH_CYLINDER',text='Cylinder')
        row.operator('mesh.primitive_uv_sphere_add',icon='MESH_UVSPHERE',text='UV Sphere')       #Mesh Operator
        row = layout.row()
        row.operator('curve.primitive_bezier_curve_add',icon='CURVE_BEZCURVE',text= 'Curve')
        row.operator('curve.primitive_bezier_circle_add',icon='CURVE_BEZCIRCLE',text='Circle')        #Curve Operator
        row = layout.row()
        op = row.operator('object.modifier_add')     #Modifier Poerator
        


 
class SHADER_OT_BackFaceBlack(bpy.types.Operator):

    bl_label = 'BackFaceBlack'
    bl_idname = 'shader.backface'


    
    def execute(self, context):     #Creating New Material 'M_BackFaceBlack' 

        if bpy.data.materials.get('M_BackFaceBlack') == None:

            M_BackFaceBlack = bpy.data.materials.new(name='M_BackFaceBlack')
            M_BackFaceBlack.use_nodes = True
            M_BackFaceBlack.node_tree.nodes.remove(M_BackFaceBlack.node_tree.nodes.get('Principled BSDF'))
            M_Output = M_BackFaceBlack.node_tree.nodes.get('Material Output')
            M_Specular=M_BackFaceBlack.node_tree.nodes.new('ShaderNodeEeveeSpecular')
            M_Specular.inputs[0].default_value = (0.319,0.319,0.319,1.000)
            M_Specular.inputs[1].default_value = (0.000,0.567,1.000,1.000)
            M_Specular.inputs[2].default_value = 0.350
            M_MixShader=M_BackFaceBlack.node_tree.nodes.new('ShaderNodeMixShader')
            M_MixShader.inputs[0].default_value = 1.000
            M_Diffuse=M_BackFaceBlack.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
            M_Diffuse.inputs[0].default_value = (0,0,0,1)
            M_Geometry=M_BackFaceBlack.node_tree.nodes.new('ShaderNodeNewGeometry')
            M_BackFaceBlack.node_tree.links.new(M_Geometry.outputs[6],M_MixShader.inputs[0])
            M_BackFaceBlack.node_tree.links.new(M_Specular.outputs[0],M_MixShader.inputs[1])
            M_BackFaceBlack.node_tree.links.new(M_Diffuse.outputs[0],M_MixShader.inputs[2])
            M_BackFaceBlack.node_tree.links.new(M_MixShader.outputs[0],M_Output.inputs[0])

        else:

            M_BackFaceBlack = bpy.data.materials.get('M_BackFaceBlack')

        bpy.context.object.active_material = M_BackFaceBlack
        bpy.ops.object.make_links_data(type= 'MATERIAL')

        return {'FINISHED'}


 
class SHADER_PT_ShaderPanel(bpy.types.Panel):    #Special Material Library Panel
    
    bl_label = 'Shaders SP'
    bl_idname = 'ShaderPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stitches'
    bl_parent_id = 'Object_Module'   
    bl_options = {'DEFAULT_CLOSED'} 
    # bl_order = 2    


    
    def draw(self,context):
        
        layout = self.layout
        row = layout.row()
        row.operator('shader.backface',icon='BRUSH_TEXFILL',text='Backface Black')


''' 
class DG_OT_MeshCube(bpy.types.Operator):     #Create Cube Dialog

    bl_label='Mesh'
    bl_idname='dg.mesh'

    

    text = bpy.props.StringProperty(name='Object name:',default="Cube")
    scale = bpy.props.FloatVectorProperty(name='Scale',default=[1,1,1])   
    
    
    def execute(self,context):

        t = self.text
        s = self.scale
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object
        obj.name = t
        obj.scale[0] = s[0]
        obj.scale[1] = s[1]
        obj.scale[2] = s[2]
        return {'FINISHED'}


    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self)
'''
 
class C_PT_EditPanel(bpy.types.Panel):     # Edit Panel
    
    
    bl_label = 'Edit'
    bl_idname = 'EditPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stitches'
    bl_parent_id = 'Object_Module'  
    # bl_order = 4   
    
    
    def draw(self,context):
        
        layout = self.layout
        row = layout.row()
        row.operator('obj.deleteobj',text='SmartDel')       #Smart Delete
        row.operator('uv.islandtohardedges')
        row = layout.row()
        cp = row.operator('object.origin_set',text = 'Center Pivot')        #Center Pivot
        cp.type = 'ORIGIN_GEOMETRY'

        if bpy.context.scene.tool_settings.use_transform_data_origin == True:        #Edit Pivot
            row.operator("pivot.transform_off_n", text="Apply") 
        else:
            row.operator("pivot.transform_on_n", text="Edit Pivot") 


        
        row = layout.row()
        
        row.operator("pivot.bounding_box_n", text="Pivot To BoundingBOX")     #Pivot To BoundingBOX
    

        row = layout.row()
        
        row.operator('mesh.customdata_custom_splitnormals_clear',text='Unblock Normal')     #Unblock Normal

        ft = row.operator('object.transform_apply',text = 'Freeze Transformations')     #Freeze Transformations
        ft.location=True
        ft.rotation=True
        ft.scale=True
        ft.properties=True
        column = self.layout.column()
        #column.label(text='shading')
        

        if bpy.context.active_object != None and bpy.context.active_object.type == 'MESH':

            column.operator('object.shade_smooth')      #Shadersmooth
            box = column.box().column()
            mesh = bpy.context.active_object.data
            box.prop(mesh, "use_auto_smooth", text="Autosmooth")             #Autosmooth       
            # row = column.row(align=True)
            # box = column.row().column()
            # box = column.box().column()
            if bpy.context.active_object.data.use_auto_smooth == True:

                box.prop(mesh, "auto_smooth_angle", text="Angle")

class C_PT_MirrorPanel(bpy.types.Panel):     # Mirror Panel
    
    
    bl_label = 'Mirror'
    bl_idname = 'MirrorPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stitches'
    bl_parent_id = 'Object_Module'  
    bl_options = {'DEFAULT_CLOSED'} 
    # bl_order = 5   
    
    
    def draw(self,context):
        
        layout = self.layout
        
        row = layout.row()
        # row.label(text='Global')
        # row = layout.row()

        mirrorX = row.operator('transform.mirror',text='X')
        mirrorX.orient_type='GLOBAL'
        mirrorX.constraint_axis=(True, False, False)

        mirrorY = row.operator('transform.mirror',text='Y')
        mirrorY.orient_type='GLOBAL'
        mirrorY.constraint_axis=(False, True, False)

        mirrorZ = row.operator('transform.mirror',text='Z')
        mirrorZ.orient_type='GLOBAL'
        mirrorZ.constraint_axis=(False, False, True)


class C_PT_OthersPanel(bpy.types.Panel):     # Mirror Panel
    
    
    bl_label = 'Others'
    bl_idname = 'OthersPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stitches'
    bl_parent_id = 'Object_Module'  
    bl_options = {'DEFAULT_CLOSED'} 

    def draw(self,context):
        
        layout = self.layout
        row = layout.row()
        # batchRename = row.operator('wm.batch_rename',text='Batch Rename Select')
        # batchRename.data_type='OBJECT'
        # batchRename.data_source='SELECT'
        # bpy.ops.wm.batch_rename(data_type='OBJECT', data_source='SELECT', actions=None)
        row.operator('object.renameobjects',text='Batch Rename')



classes = [

MAIN_PT_Stitches_Obj,
C_PT_FilePanel,
SHADER_OT_BackFaceBlack ,
SHADER_PT_ShaderPanel,
C_PT_MirrorPanel,
C_PT_OthersPanel,
C_PT_MCPanel,
# DG_OT_MeshCube,
C_PT_EditPanel,
UV_OT_Island2HardEdges,

 
]



def register():
    
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():   
    
     for cls in classes:
        bpy.utils.unregister_class(cls)


