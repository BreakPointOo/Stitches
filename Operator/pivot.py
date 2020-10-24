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


'''
bl_info = {
    'name': 'Pivot Transform',
    #"description": "This is a test version of the addon. Write in the discord channel(link below) about the errors."
    "author": "Max Derksen",
    'version': (1, 4, 4), 
    'blender': (2, 81, 0),
    'location': 'VIEW 3D > N-Panel > Pivot Point Popover',
    #"warning": "This is a test version of the addon. Write in the discord channel(link below) about the errors.",
    "support": "COMMUNITY",
    'category': 'Object',
}
'''


import bpy
import re 
import bmesh 
import mathutils
from mathutils import Matrix, Vector
from bpy.types import Operator

from bpy.props import IntProperty, FloatProperty #Bounding Box


#========================================================================PIVOT TRANSFORM TOOL IN EDIT MODE 
storeGT = False
storeGR = False
storeGS = False


class PIVOT_OT_transform_on_N(Operator):
    bl_idname = "pivot.transform_on_n"
    bl_label = "Transform"
    bl_description = "Start Pivot Transformation"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if context.scene.tool_settings.use_transform_data_origin == False:
            props_pivot = context.preferences.addons[__name__.split(".")[0]].preferences

            global storeGT
            global storeGR
            global storeGS

            storeGT = context.space_data.show_gizmo_object_translate
            storeGR = context.space_data.show_gizmo_object_rotate 
            storeGS = context.space_data.show_gizmo_object_scale 

            #if props_pivot.gizmo_preselect == True:
                #context.space_data.show_gizmo_object_translate = props_pivot.move_giz
                #context.space_data.show_gizmo_object_rotate = props_pivot.rotate_giz
                #context.space_data.show_gizmo_object_scale = props_pivot.scale_giz



            if context.mode != 'OBJECT': 
                bpy.ops.object.mode_set(mode='OBJECT')
            
                
            context.scene.tool_settings.use_transform_data_origin = True
            return{'FINISHED'}
        else:
            return{'CANCELLED'}



class PIVOT_OT_transform_off_N(Operator):
    bl_idname = "pivot.transform_off_n"
    bl_label = "Apply"
    bl_description = "Apply Pivot Transformation"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if context.scene.tool_settings.use_transform_data_origin == True:
            global storeGT
            global storeGR
            global storeGS

            context.space_data.show_gizmo_object_translate = storeGT
            context.space_data.show_gizmo_object_rotate = storeGR
            context.space_data.show_gizmo_object_scale = storeGS

            if context.mode != 'OBJECT': 
                bpy.ops.object.mode_set(mode='OBJECT')

            context.scene.tool_settings.use_transform_data_origin = False
            return{'FINISHED'}
        else:
            return{'CANCELLED'}



import bgl 
import gpu
from gpu_extras.batch import batch_for_shader



def ob_add(self, context, obj):
    """ bpy.ops.mesh.primitive_cube_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
    bbox = context.active_object
    bbox.matrix_world = self.obj.matrix_world
    bm = bmesh.from_edit_mesh(bbox.data)
    
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()


    for i, vert in enumerate(ob_bbox):
        
        
        bm.verts[i].co = (vert[0], vert[1], vert[2])

    
    #bm.to_mesh(me)
    
    bpy.ops.mesh.select_all(action='DESELECT') """
    
    ob_bbox = obj.bound_box

    me = bpy.data.meshes.new('PivotBBox')
    bbox = bpy.data.objects.new('PivotBBox', me)
    bbox.matrix_world = obj.matrix_world
    

    context.collection.objects.link(bbox)
    bm = bmesh.new()
    bm.from_mesh(me)

    for vert in ob_bbox:
        bm.verts.new(vert[:])
    
    vertex=[]
    for v in bm.verts:           
        vertex.append(v)   
    
    bm.faces.new((vertex[0], vertex[1], vertex[2], vertex[3]))
    bm.faces.new((vertex[3], vertex[2], vertex[6], vertex[7]))
    bm.faces.new((vertex[3], vertex[7], vertex[4], vertex[0]))
    bm.faces.new((vertex[4], vertex[5], vertex[6], vertex[7]))
    bm.faces.new((vertex[2], vertex[1], vertex[5], vertex[6]))
    bm.faces.new((vertex[0], vertex[4], vertex[5], vertex[1]))
    
    bm.to_mesh(me) 

    

    bpy.ops.object.select_all(action='DESELECT')
    bbox.select_set(state=True) 
    context.view_layer.objects.active = bbox 

    context.object.display_type = 'WIRE'


    bpy.ops.object.mode_set(mode='EDIT')
    context.tool_settings.mesh_select_mode = (True, True, True)

    obj.select_set(state=True)



class PIVOT_OT_bounding_box_N(Operator):
    bl_idname = "pivot.bounding_box_n"
    bl_label = "Pivot To Bounding Box"
    bl_description = "Apply Transformation"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
       return context.active_object is not None
    

    def __init__(self):
        self.obj = None
        self.select_mode = tuple()


    @staticmethod
    def draw_mesh(self, context):
        shader = gpu.shader.from_builtin('3D_SMOOTH_COLOR')
        theme = bpy.context.preferences.themes['Default']
        vertex_size = theme.view_3d.vertex_size


        bgl.glEnable(bgl.GL_BLEND)
        bgl.glLineWidth(3)
        bgl.glPointSize(vertex_size + 4)

        bgl.glEnable(bgl.GL_DEPTH_TEST)
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        bgl.glEnable(bgl.GL_CULL_FACE)
        bgl.glCullFace(bgl.GL_BACK)
                
                
        bgl.glDepthRange(0, 0.9999) 
        bgl.glDepthMask(False)

        shader.bind()

        bbox = context.active_object
        mesh = bmesh.from_edit_mesh(bbox.data)



        vertex_co = [bbox.matrix_world @ v.co for v in mesh.verts]

        vertex_all = []
        for e in mesh.edges:
            v1 = bbox.matrix_world @ e.verts[0].co
            v2 = bbox.matrix_world @ e.verts[1].co
            vCo = (v1 + v2) / 2
            vertex_all.append(vCo)

        for f in mesh.faces:
            vCo = bbox.matrix_world @ f.calc_center_bounds()
            vertex_all.append(vCo)

        for v in vertex_co:
            vertex_all.append(v)


        edge_keys = bbox.data.edge_keys

        loop_triangles = mesh.calc_loop_triangles()
        faces_indices = [[loop.vert.index for loop in looptris] for looptris in loop_triangles]

        face_col = [(0.2, 0.2, 0.2, 0.6) for _ in range(len(vertex_co))]
        edge_col = [(0.1, 0.1, 0.1, 1.0) for _ in range(len(vertex_co))]
        vert_col = [(0.1, 0.4, 1.0, 1.0) for _ in range(len(vertex_all))]


        FACES = batch_for_shader(shader, 'TRIS', {"pos": vertex_co, "color": face_col}, indices=faces_indices)
        EDGES = batch_for_shader(shader, 'LINES', {"pos": vertex_co, "color": edge_col}, indices=edge_keys) 
        VERTS = batch_for_shader(shader, 'POINTS', {"pos": vertex_all, "color": vert_col}) 
    

        FACES.draw(shader)
        EDGES.draw(shader)
        VERTS.draw(shader)


        bgl.glDepthRange(0, 1) 
        bgl.glDisable(bgl.GL_LINE_SMOOTH)
        bgl.glDisable(bgl.GL_DEPTH_TEST)
        bgl.glDisable(bgl.GL_CULL_FACE)
        bgl.glLineWidth(1)
        bgl.glPointSize(vertex_size)
        bgl.glDisable(bgl.GL_BLEND)  


    def modal(self, context, event):
        props_pivot = context.preferences.addons[__name__.split(".")[0]].preferences
        if context.area:
            if context.area.type == 'VIEW_3D':
                #context.area.tag_redraw()

                # Selected Object(EDIT_MODE)  
                bbox = context.active_object
                me = bmesh.from_edit_mesh(bbox.data)
                    
                # select items
                verts_sel = []
                verts_sel.extend([v for v in me.verts if v.select]) 

            
                if len(verts_sel) >= 1:
                    #bpy.ops.pivot.alignface()
                    cursor_pos = context.scene.cursor.location.copy()
                    bpy.ops.view3d.snap_cursor_to_selected()

                    context.tool_settings.mesh_select_mode = self.select_mode
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

                    bpy.context.collection.objects.unlink(bbox)
                    bpy.ops.object.delete({"selected_objects": [bbox]})                            
                            
                    context.view_layer.objects.active = self.obj
                    context.scene.cursor.location = cursor_pos

                    bpy.types.SpaceView3D.draw_handler_remove(self._bb_mesh_draw, 'WINDOW')
                    #props_pivot.bbox_run = False
                    return {'FINISHED'}


                if not event.type in {'RIGHTMOUSE', 'MIDLEMOUSE', 'LEFTMOUSE'} and event.value == 'PRESS':
                  
                    #props_pivot.bbox_run = False


                    context.tool_settings.mesh_select_mode = self.select_mode
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.context.collection.objects.unlink(bbox)
                    bpy.ops.object.delete({"selected_objects": [bbox]})                               
                    context.view_layer.objects.active = self.obj
                
                    bpy.types.SpaceView3D.draw_handler_remove(self._bb_mesh_draw, 'WINDOW')
                    return {'CANCELLED'}
                
                    
                
                
        else:
            #props_pivot.bbox_run = False
            bpy.types.SpaceView3D.draw_handler_remove(self._bb_mesh_draw, 'WINDOW')
            return {'FINISHED'}

        return {'PASS_THROUGH'}
       

    def invoke(self, context, event):
        if context.mode != 'OBJECT': 
            bpy.ops.object.mode_set(mode='OBJECT')


        props_pivot = context.preferences.addons[__name__.split(".")[0]].preferences
        #props_pivot.bbox_run = True


        self.select_mode = context.tool_settings.mesh_select_mode[:]
          

        self.obj = context.active_object
        
        ob_add(self, context, self.obj)
        

        if context.area.type == 'VIEW_3D':
            args = (self, context)
            self._bb_mesh_draw= bpy.types.SpaceView3D.draw_handler_add(self.draw_mesh, args, 'WINDOW', 'POST_VIEW')
        context.window_manager.modal_handler_add(self) 
        return {'RUNNING_MODAL'}
   
    




classes = [
    
    PIVOT_OT_transform_on_N,
    PIVOT_OT_transform_off_N,
    PIVOT_OT_bounding_box_N,
]

def register():
    global storeGT
    global storeGR
    global storeGS


    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)                                                                                                                       