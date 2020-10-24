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

class Stitches_UV(bpy.types.Panel):
    
    bl_label = 'UV_Module'
    bl_idname = 'UV_Module'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Stitches'
    
    def draw(self,contex):
        
        layout = self.layout
        row = layout.row()

class UV_PT_Edit(bpy.types.Panel):

    bl_label = 'Edit'
    bl_idname = 'uv.edit'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Stitches'
    bl_parent_id = 'UV_Module'

    def draw(self,contex):
        
        layout = self.layout
        # box = layout.box()
        # row = box.row()
        # MarkSeam = row.operator('uv.mark_seam',text='Mark Seam')
        # MarkSeam.clear=False
        # ClearSeam = row.operator('uv.mark_seam',text='Clear Seam')
        # ClearSeam.clear=True
        
        row = layout.row()
        row.operator('uv.alignuv')
        box = layout.box()
        row = box.row()
        row.operator('uv.pack',text='Pack UV Island')
        scene = bpy.context.scene
        tool = scene.uv_tool
        row.prop(tool,"my_bool", text="Rotate")
        box.prop(tool,"my_float", text="Threshold")
        
        # bpy.ops.uv.muv_select_uv_select_overlapped()
        # bpy.ops.uv.muv_select_uv_select_flipped()
        row = layout.row()
        row.operator('uv.muv_select_uv_select_overlapped',text='Select Overlapped')
        row.operator('uv.muv_select_uv_select_flipped',text='Select Flipped')
        # bpy.ops.uv.uv_face_rip()
        # bpy.ops.uv.select_split()

        row = layout.row()
        row.operator('uv.select_split',text='Split')
        stitch = row.operator('uv.stitch')
        stitch.snap_islands=True
        stitch.clear_seams=True
        row = layout.row()
        row.operator('uv.weld')
        # bpy.ops.uv.stitch(use_limit=False, snap_islands=True, limit=0.01, static_island=0, active_object_index=0, midpoint_snap=False, clear_seams=True, mode='EDGE', stored_mode='EDGE', selection=[], objects_selection_count=(0, ))
        box = layout.box()
        row = box.row()
        # row = layout.row()
        row.label(text='Align')
        # bpy.ops.uv.align(axis='ALIGN_AUTO')
        # bpy.ops.uv.align(axis='ALIGN_S')
        # bpy.ops.uv.align(axis='ALIGN_T')
        # bpy.ops.uv.align(axis='ALIGN_U')
        # bpy.ops.uv.align(axis='ALIGN_X')
        # bpy.ops.uv.align(axis='ALIGN_Y')
        row = box.row()
        AlignAuto = row.operator('uv.align',text='Auto')
        AlignAuto.axis='ALIGN_AUTO'
        AlignX = row.operator('uv.align',text='X')
        AlignX.axis='ALIGN_X'
        AlignY = row.operator('uv.align',text='Y')
        AlignY.axis='ALIGN_Y'
        # bpy.ops.transform.mirror(constraint_axis=(True, False, False))
        row = layout.row()
        MirrorX = row.operator('transform.mirror',text='Mirror X')
        MirrorX.constraint_axis=(True, False, False)
        MirrorY = row.operator('transform.mirror',text='Mirror Y')
        MirrorY.constraint_axis=(False, True, False)






classes = [

    Stitches_UV,
    UV_PT_Edit,
    
]


def register():
    
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():   
    
     for cls in classes:
        bpy.utils.unregister_class(cls)
        
