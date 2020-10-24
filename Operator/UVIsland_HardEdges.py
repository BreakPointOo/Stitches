

'''bl_info = {
    "name": "UVs_to_Hard_Edges",
    "author": "Ferran M.Clar, 2.80 update NecroFriedChicken",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "3D View -> Tools Panel",
    "description": "Sets the object UV islands borders' edges to hard edges and an Edge Split modifier",
    "category": "Object"}
'''



import bpy
import bmesh


class UV_OT_Island2HardEdges(bpy.types.Operator):
    bl_idname = "uv.islandtohardedges"
    bl_label = "UVIslandToHardEdges"
    bl_description = "Sets the object UV islands borders' edges to hard edges and an Edge Split modifier"
    # bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):
        if context.active_object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode = 'EDIT')
            
        bpy.ops.uv.seams_from_islands()

        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        mesh = bpy.context.object.data
        
        bm = bmesh.new()
        bm.from_mesh(mesh)

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        edges = []

        for edge in bm.edges:
            
            if edge.seam:
                edge.smooth = False


        bpy.ops.object.mode_set(mode = 'OBJECT')

        bm.to_mesh(mesh)
        bm.free()

        
        return {'FINISHED'}