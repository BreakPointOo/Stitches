import bmesh
import bpy
import collections
import mathutils
import math
from bpy_extras import view3d_utils
from bpy.types import (
        Operator,
        Menu,
        Panel,
        PropertyGroup,
        AddonPreferences,
        )
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        )

looptools_cache = {}



# calculate the determinant of a matrix
def matrix_determinant(m):
    determinant = m[0][0] * m[1][1] * m[2][2] + m[0][1] * m[1][2] * m[2][0] \
        + m[0][2] * m[1][0] * m[2][1] - m[0][2] * m[1][1] * m[2][0] \
        - m[0][1] * m[1][0] * m[2][2] - m[0][0] * m[1][2] * m[2][1]

    return(determinant)


# custom matrix inversion, to provide higher precision than the built-in one
def matrix_invert(m):
    r = mathutils.Matrix((
        (m[1][1] * m[2][2] - m[1][2] * m[2][1], m[0][2] * m[2][1] - m[0][1] * m[2][2],
         m[0][1] * m[1][2] - m[0][2] * m[1][1]),
        (m[1][2] * m[2][0] - m[1][0] * m[2][2], m[0][0] * m[2][2] - m[0][2] * m[2][0],
         m[0][2] * m[1][0] - m[0][0] * m[1][2]),
        (m[1][0] * m[2][1] - m[1][1] * m[2][0], m[0][1] * m[2][0] - m[0][0] * m[2][1],
         m[0][0] * m[1][1] - m[0][1] * m[1][0])))

    return (r * (1 / matrix_determinant(m)))


def edgekey(edge):
    return(tuple(sorted([edge.verts[0].index, edge.verts[1].index])))
def initialise():
    object = bpy.context.active_object
    if 'MIRROR' in [mod.type for mod in object.modifiers if mod.show_viewport]:
        # ensure that selection is synced for the derived mesh
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(object.data)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    return(object, bm)   

    # force a full recalculation next time
def cache_delete(tool):
    if tool in looptools_cache:
        del looptools_cache[tool]

# returns the edgekeys of a bmesh face
def face_edgekeys(face):
    return([tuple(sorted([edge.verts[0].index, edge.verts[1].index])) for edge in face.edges])

# check cache for stored information
def cache_read(tool, object, bm, input_method, boundaries):
    # current tool not cached yet
    if tool not in looptools_cache:
        return(False, False, False, False, False)
    # check if selected object didn't change
    if object.name != looptools_cache[tool]["object"]:
        return(False, False, False, False, False)
    # check if input didn't change
    if input_method != looptools_cache[tool]["input_method"]:
        return(False, False, False, False, False)
    if boundaries != looptools_cache[tool]["boundaries"]:
        return(False, False, False, False, False)
    modifiers = [mod.name for mod in object.modifiers if mod.show_viewport and
                 mod.type == 'MIRROR']
    if modifiers != looptools_cache[tool]["modifiers"]:
        return(False, False, False, False, False)
    input = [v.index for v in bm.verts if v.select and not v.hide]
    if input != looptools_cache[tool]["input"]:
        return(False, False, False, False, False)
    # reading values
    single_loops = looptools_cache[tool]["single_loops"]
    loops = looptools_cache[tool]["loops"]
    derived = looptools_cache[tool]["derived"]
    mapping = looptools_cache[tool]["mapping"]

    return(True, single_loops, loops, derived, mapping)

# store information in the cache
def cache_write(tool, object, bm, input_method, boundaries, single_loops,
loops, derived, mapping):
    # clear cache of current tool
    if tool in looptools_cache:
        del looptools_cache[tool]
    # prepare values to be saved to cache
    input = [v.index for v in bm.verts if v.select and not v.hide]
    modifiers = [mod.name for mod in object.modifiers if mod.show_viewport
    and mod.type == 'MIRROR']
    # update cache
    looptools_cache[tool] = {
        "input": input, "object": object.name,
        "input_method": input_method, "boundaries": boundaries,
        "single_loops": single_loops, "loops": loops,
        "derived": derived, "mapping": mapping, "modifiers": modifiers}

# calculate a best-fit plane to the given vertices
def calculate_plane(bm_mod, loop, method="best_fit", object=False):
    # getting the vertex locations
    locs = [bm_mod.verts[v].co.copy() for v in loop[0]]

    # calculating the center of masss
    com = mathutils.Vector()
    for loc in locs:
        com += loc
    com /= len(locs)
    x, y, z = com

    if method == 'best_fit':
        # creating the covariance matrix
        mat = mathutils.Matrix(((0.0, 0.0, 0.0),
                                (0.0, 0.0, 0.0),
                                (0.0, 0.0, 0.0),
                                ))
        for loc in locs:
            mat[0][0] += (loc[0] - x) ** 2
            mat[1][0] += (loc[0] - x) * (loc[1] - y)
            mat[2][0] += (loc[0] - x) * (loc[2] - z)
            mat[0][1] += (loc[1] - y) * (loc[0] - x)
            mat[1][1] += (loc[1] - y) ** 2
            mat[2][1] += (loc[1] - y) * (loc[2] - z)
            mat[0][2] += (loc[2] - z) * (loc[0] - x)
            mat[1][2] += (loc[2] - z) * (loc[1] - y)
            mat[2][2] += (loc[2] - z) ** 2

        # calculating the normal to the plane
        normal = False
        try:
            mat = matrix_invert(mat)
        except:
            ax = 2
            if math.fabs(sum(mat[0])) < math.fabs(sum(mat[1])):
                if math.fabs(sum(mat[0])) < math.fabs(sum(mat[2])):
                    ax = 0
            elif math.fabs(sum(mat[1])) < math.fabs(sum(mat[2])):
                ax = 1
            if ax == 0:
                normal = mathutils.Vector((1.0, 0.0, 0.0))
            elif ax == 1:
                normal = mathutils.Vector((0.0, 1.0, 0.0))
            else:
                normal = mathutils.Vector((0.0, 0.0, 1.0))
        if not normal:
            # warning! this is different from .normalize()
            itermax = 500
            vec2 = mathutils.Vector((1.0, 1.0, 1.0))
            for i in range(itermax):
                vec = vec2
                vec2 = mat @ vec
                # Calculate length with double precision to avoid problems with `inf`
                vec2_length = math.sqrt(vec2[0] ** 2 + vec2[1] ** 2 + vec2[2] ** 2)
                if vec2_length != 0:
                    vec2 /= vec2_length
                if vec2 == vec:
                    break
            if vec2.length == 0:
                vec2 = mathutils.Vector((1.0, 1.0, 1.0))
            normal = vec2

    elif method == 'normal':
        # averaging the vertex normals
        v_normals = [bm_mod.verts[v].normal for v in loop[0]]
        normal = mathutils.Vector()
        for v_normal in v_normals:
            normal += v_normal
        normal /= len(v_normals)
        normal.normalize()

    elif method == 'view':
        # calculate view normal
        rotation = bpy.context.space_data.region_3d.view_matrix.to_3x3().\
            inverted()
        normal = rotation @ mathutils.Vector((0.0, 0.0, 1.0))
        if object:
            normal = object.matrix_world.inverted().to_euler().to_matrix() @ \
                     normal

    return(com, normal)

# input: bmesh, output: dict with the vert index as key and edge-keys as value
def dict_vert_edges(bm):
    vert_edges = dict([[v.index, []] for v in bm.verts if not v.hide])
    for edge in bm.edges:
        if edge.hide:
            continue
        ek = edgekey(edge)
        for vert in ek:
            vert_edges[vert].append(ek)

    return(vert_edges)


# input: bmesh, output: dict with the vert index as key and face index as value
def dict_vert_faces(bm):
    vert_faces = dict([[v.index, []] for v in bm.verts if not v.hide])
    for face in bm.faces:
        if not face.hide:
            for vert in face.verts:
                vert_faces[vert.index].append(face.index)

    return(vert_faces)


# input: list of edge-keys, output: dictionary with vertex-vertex connections
def dict_vert_verts(edge_keys):
    # create connection data
    vert_verts = {}
    for ek in edge_keys:
        for i in range(2):
            if ek[i] in vert_verts:
                vert_verts[ek[i]].append(ek[1 - i])
            else:
                vert_verts[ek[i]] = [ek[1 - i]]

    return(vert_verts)

# check loops and only return valid ones
def check_loops(loops, mapping, bm_mod):
    valid_loops = []
    for loop, circular in loops:
        # loop needs to have at least 3 vertices
        if len(loop) < 3:
            continue
        # loop needs at least 1 vertex in the original, non-mirrored mesh
        if mapping:
            all_virtual = True
            for vert in loop:
                if mapping[vert] > -1:
                    all_virtual = False
                    break
            if all_virtual:
                continue
        # vertices can not all be at the same location
        stacked = True
        for i in range(len(loop) - 1):
            if (bm_mod.verts[loop[i]].co - bm_mod.verts[loop[i + 1]].co).length > 1e-6:
                stacked = False
                break
        if stacked:
            continue
        # passed all tests, loop is valid
        valid_loops.append([loop, circular])

    return(valid_loops)

# move the vertices to their new locations
def move_verts(object, bm, mapping, move, lock, influence):
    if lock:
        lock_x, lock_y, lock_z = lock
        orient_slot = bpy.context.scene.transform_orientation_slots[0]
        custom = orient_slot.custom_orientation
        if custom:
            mat = custom.matrix.to_4x4().inverted() @ object.matrix_world.copy()
        elif orient_slot.type == 'LOCAL':
            mat = mathutils.Matrix.Identity(4)
        elif orient_slot.type == 'VIEW':
            mat = bpy.context.region_data.view_matrix.copy() @ \
                object.matrix_world.copy()
        else:  # orientation == 'GLOBAL'
            mat = object.matrix_world.copy()
        mat_inv = mat.inverted()

    for loop in move:
        for index, loc in loop:
            if mapping:
                if mapping[index] == -1:
                    continue
                else:
                    index = mapping[index]
            if lock:
                delta = (loc - bm.verts[index].co) @ mat_inv
                if lock_x:
                    delta[0] = 0
                if lock_y:
                    delta[1] = 0
                if lock_z:
                    delta[2] = 0
                delta = delta @ mat
                loc = bm.verts[index].co + delta
            if influence < 0:
                new_loc = loc
            else:
                new_loc = loc * (influence / 100) + \
                                 bm.verts[index].co * ((100 - influence) / 100)
            bm.verts[index].co = new_loc
    bm.normal_update()
    object.data.update()

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

# sorts all edge-keys into a list of loops
def get_connected_selections(edge_keys):
    # create connection data
    vert_verts = dict_vert_verts(edge_keys)

    # find loops consisting of connected selected edges
    loops = []
    while len(vert_verts) > 0:
        loop = [iter(vert_verts.keys()).__next__()]
        growing = True
        flipped = False

        # extend loop
        while growing:
            # no more connection data for current vertex
            if loop[-1] not in vert_verts:
                if not flipped:
                    loop.reverse()
                    flipped = True
                else:
                    growing = False
            else:
                extended = False
                for i, next_vert in enumerate(vert_verts[loop[-1]]):
                    if next_vert not in loop:
                        vert_verts[loop[-1]].pop(i)
                        if len(vert_verts[loop[-1]]) == 0:
                            del vert_verts[loop[-1]]
                        # remove connection both ways
                        if next_vert in vert_verts:
                            if len(vert_verts[next_vert]) == 1:
                                del vert_verts[next_vert]
                            else:
                                vert_verts[next_vert].remove(loop[-1])
                        loop.append(next_vert)
                        extended = True
                        break
                if not extended:
                    # found one end of the loop, continue with next
                    if not flipped:
                        loop.reverse()
                        flipped = True
                    # found both ends of the loop, stop growing
                    else:
                        growing = False

        # check if loop is circular
        if loop[0] in vert_verts:
            if loop[-1] in vert_verts[loop[0]]:
                # is circular
                if len(vert_verts[loop[0]]) == 1:
                    del vert_verts[loop[0]]
                else:
                    vert_verts[loop[0]].remove(loop[-1])
                if len(vert_verts[loop[-1]]) == 1:
                    del vert_verts[loop[-1]]
                else:
                    vert_verts[loop[-1]].remove(loop[0])
                loop = [loop, True]
            else:
                # not circular
                loop = [loop, False]
        else:
            # not circular
            loop = [loop, False]

        loops.append(loop)

    return(loops)

# clean up and set settings back to original state
def terminate():
    # update editmesh cached data
    obj = bpy.context.active_object
    if obj.mode == 'EDIT':
        bmesh.update_edit_mesh(obj.data, loop_triangles=True, destructive=True)

# def settings_load(self):
#     lt = bpy.context.window_manager.looptools
#     tool = self.name.split()[0].lower()
#     keys = self.as_keywords().keys()
#     for key in keys:
#         setattr(self, key, getattr(lt, tool + "_" + key))


# returns the edgekeys of a bmesh face
# sort input into loops
def flatten_get_input(bm):
    vert_verts = dict_vert_verts(
            [edgekey(edge) for edge in bm.edges if edge.select and not edge.hide]
            )
    verts = [v.index for v in bm.verts if v.select and not v.hide]

    # no connected verts, consider all selected verts as a single input
    if not vert_verts:
        return([[verts, False]])

    loops = []
    while len(verts) > 0:
        # start of loop
        loop = [verts[0]]
        verts.pop(0)
        if loop[-1] in vert_verts:
            to_grow = vert_verts[loop[-1]]
        else:
            to_grow = []
        # grow loop
        while len(to_grow) > 0:
            new_vert = to_grow[0]
            to_grow.pop(0)
            if new_vert in loop:
                continue
            loop.append(new_vert)
            verts.remove(new_vert)
            to_grow += vert_verts[new_vert]
        # add loop to loops
        loops.append([loop, False])

    return(loops)

# calculate position of vertex projections on plane
def flatten_project(bm, loop, com, normal):
    verts = [bm.verts[v] for v in loop[0]]
    verts_projected = [
        [v.index, mathutils.Vector(v.co[:]) -
        (mathutils.Vector(v.co[:]) - com).dot(normal) * normal] for v in verts
        ]

    return(verts_projected)

# get the derived mesh data, if there is a mirror modifier
def get_derived_bmesh(object, bm, not_use_mirror):
    # check for mirror modifiers
    if 'MIRROR' in [mod.type for mod in object.modifiers if mod.show_viewport]:
        derived = True
        # disable other modifiers
        show_viewport = [mod.name for mod in object.modifiers if mod.show_viewport]
        merge = []
        for mod in object.modifiers:
            if mod.type != 'MIRROR':
                mod.show_viewport = False
            #leave the merge points untouched
            if mod.type == 'MIRROR':
                merge.append(mod.use_mirror_merge)
                if not_use_mirror:
                    mod.use_mirror_merge = False
        # get derived mesh
        bm_mod = bmesh.new()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        object_eval = object.evaluated_get(depsgraph)
        mesh_mod = object_eval.to_mesh()
        bm_mod.from_mesh(mesh_mod)
        object_eval.to_mesh_clear()
        # re-enable other modifiers
        for mod_name in show_viewport:
            object.modifiers[mod_name].show_viewport = True
        merge.reverse()
        for mod in object.modifiers:
            if mod.type == 'MIRROR':
                mod.use_mirror_merge = merge.pop()
    # no mirror modifiers, so no derived mesh necessary
    else:
        derived = False
        bm_mod = bm

    bm_mod.verts.ensure_lookup_table()
    bm_mod.edges.ensure_lookup_table()
    bm_mod.faces.ensure_lookup_table()

    return(derived, bm_mod)

# calculate input loops
def circle_get_input(object, bm):
    # get mesh with modifiers applied
    derived, bm_mod = get_derived_bmesh(object, bm, False)

    # create list of edge-keys based on selection state
    faces = False
    for face in bm.faces:
        if face.select and not face.hide:
            faces = True
            break
    if faces:
        # get selected, non-hidden , non-internal edge-keys
        eks_selected = [
            key for keys in [face_edgekeys(face) for face in
            bm_mod.faces if face.select and not face.hide] for key in keys
            ]
        edge_count = {}
        for ek in eks_selected:
            if ek in edge_count:
                edge_count[ek] += 1
            else:
                edge_count[ek] = 1
        edge_keys = [
            edgekey(edge) for edge in bm_mod.edges if edge.select and
            not edge.hide and edge_count.get(edgekey(edge), 1) == 1
            ]
    else:
        # no faces, so no internal edges either
        edge_keys = [
            edgekey(edge) for edge in bm_mod.edges if edge.select and not edge.hide
            ]

    # add edge-keys around single vertices
    verts_connected = dict(
        [[vert, 1] for edge in [edge for edge in
        bm_mod.edges if edge.select and not edge.hide] for vert in
        edgekey(edge)]
        )
    single_vertices = [
        vert.index for vert in bm_mod.verts if
        vert.select and not vert.hide and
        not verts_connected.get(vert.index, False)
        ]

    if single_vertices and len(bm.faces) > 0:
        vert_to_single = dict(
            [[v.index, []] for v in bm_mod.verts if not v.hide]
            )
        for face in [face for face in bm_mod.faces if not face.select and not face.hide]:
            for vert in face.verts:
                vert = vert.index
                if vert in single_vertices:
                    for ek in face_edgekeys(face):
                        if vert not in ek:
                            edge_keys.append(ek)
                            if vert not in vert_to_single[ek[0]]:
                                vert_to_single[ek[0]].append(vert)
                            if vert not in vert_to_single[ek[1]]:
                                vert_to_single[ek[1]].append(vert)
                    break

    # sort edge-keys into loops
    loops = get_connected_selections(edge_keys)

    # find out to which loops the single vertices belong
    single_loops = dict([[i, []] for i in range(len(loops))])
    if single_vertices and len(bm.faces) > 0:
        for i, [loop, circular] in enumerate(loops):
            for vert in loop:
                if vert_to_single[vert]:
                    for single in vert_to_single[vert]:
                        if single not in single_loops[i]:
                            single_loops[i].append(single)

    return(derived, bm_mod, single_vertices, single_loops, loops)

# shift loop, so the first vertex is closest to the center
def circle_shift_loop(bm_mod, loop, com):
    verts, circular = loop
    distances = [
             [(bm_mod.verts[vert].co - com).length, i] for i, vert in enumerate(verts)
            ]
    distances.sort()
    shift = distances[0][1]
    loop = [verts[shift:] + verts[:shift], circular]

    return(loop)

# convert 3d coordinates to 2d coordinates on plane
def circle_3d_to_2d(bm_mod, loop, com, normal):
    # project vertices onto the plane
    verts = [bm_mod.verts[v] for v in loop[0]]
    verts_projected = [[v.co - (v.co - com).dot(normal) * normal, v.index]
                       for v in verts]

    # calculate two vectors (p and q) along the plane
    m = mathutils.Vector((normal[0] + 1.0, normal[1], normal[2]))
    p = m - (m.dot(normal) * normal)
    if p.dot(p) < 1e-6:
        m = mathutils.Vector((normal[0], normal[1] + 1.0, normal[2]))
        p = m - (m.dot(normal) * normal)
    q = p.cross(normal)

    # change to 2d coordinates using perpendicular projection
    locs_2d = []
    for loc, vert in verts_projected:
        vloc = loc - com
        x = p.dot(vloc) / p.dot(p)
        y = q.dot(vloc) / q.dot(q)
        locs_2d.append([x, y, vert])

    return(locs_2d, p, q)

# calculate a best-fit circle to the 2d locations on the plane
def circle_calculate_best_fit(locs_2d):
    # initial guess
    x0 = 0.0
    y0 = 0.0
    r = 1.0

    # calculate center and radius (non-linear least squares solution)
    for iter in range(500):
        jmat = []
        k = []
        for v in locs_2d:
            d = (v[0] ** 2 - 2.0 * x0 * v[0] + v[1] ** 2 - 2.0 * y0 * v[1] + x0 ** 2 + y0 ** 2) ** 0.5
            jmat.append([(x0 - v[0]) / d, (y0 - v[1]) / d, -1.0])
            k.append(-(((v[0] - x0) ** 2 + (v[1] - y0) ** 2) ** 0.5 - r))
        jmat2 = mathutils.Matrix(((0.0, 0.0, 0.0),
                                  (0.0, 0.0, 0.0),
                                  (0.0, 0.0, 0.0),
                                  ))
        k2 = mathutils.Vector((0.0, 0.0, 0.0))
        for i in range(len(jmat)):
            k2 += mathutils.Vector(jmat[i]) * k[i]
            jmat2[0][0] += jmat[i][0] ** 2
            jmat2[1][0] += jmat[i][0] * jmat[i][1]
            jmat2[2][0] += jmat[i][0] * jmat[i][2]
            jmat2[1][1] += jmat[i][1] ** 2
            jmat2[2][1] += jmat[i][1] * jmat[i][2]
            jmat2[2][2] += jmat[i][2] ** 2
        jmat2[0][1] = jmat2[1][0]
        jmat2[0][2] = jmat2[2][0]
        jmat2[1][2] = jmat2[2][1]
        try:
            jmat2.invert()
        except:
            pass
        dx0, dy0, dr = jmat2 @ k2
        x0 += dx0
        y0 += dy0
        r += dr
        # stop iterating if we're close enough to optimal solution
        if abs(dx0) < 1e-6 and abs(dy0) < 1e-6 and abs(dr) < 1e-6:
            break

    # return center of circle and radius
    return(x0, y0, r)

# calculate circle so no vertices have to be moved away from the center
def circle_calculate_min_fit(locs_2d):
    # center of circle
    x0 = (min([i[0] for i in locs_2d]) + max([i[0] for i in locs_2d])) / 2.0
    y0 = (min([i[1] for i in locs_2d]) + max([i[1] for i in locs_2d])) / 2.0
    center = mathutils.Vector([x0, y0])
    # radius of circle
    r = min([(mathutils.Vector([i[0], i[1]]) - center).length for i in locs_2d])

    # return center of circle and radius
    return(x0, y0, r)

# calculate the new locations of the vertices that need to be moved
def circle_calculate_verts(flatten, bm_mod, locs_2d, com, p, q, normal):
    # changing 2d coordinates back to 3d coordinates
    locs_3d = []
    for loc in locs_2d:
        locs_3d.append([loc[2], loc[0] * p + loc[1] * q + com])

    if flatten:  # flat circle
        return(locs_3d)

    else:  # project the locations on the existing mesh
        vert_edges = dict_vert_edges(bm_mod)
        vert_faces = dict_vert_faces(bm_mod)
        faces = [f for f in bm_mod.faces if not f.hide]
        rays = [normal, -normal]
        new_locs = []
        for loc in locs_3d:
            projection = False
            if bm_mod.verts[loc[0]].co == loc[1]:  # vertex hasn't moved
                projection = loc[1]
            else:
                dif = normal.angle(loc[1] - bm_mod.verts[loc[0]].co)
                if -1e-6 < dif < 1e-6 or math.pi - 1e-6 < dif < math.pi + 1e-6:
                    # original location is already along projection normal
                    projection = bm_mod.verts[loc[0]].co
                else:
                    # quick search through adjacent faces
                    for face in vert_faces[loc[0]]:
                        verts = [v.co for v in bm_mod.faces[face].verts]
                        if len(verts) == 3:  # triangle
                            v1, v2, v3 = verts
                            v4 = False
                        else:  # assume quad
                            v1, v2, v3, v4 = verts[:4]
                        for ray in rays:
                            intersect = mathutils.geometry.\
                            intersect_ray_tri(v1, v2, v3, ray, loc[1])
                            if intersect:
                                projection = intersect
                                break
                            elif v4:
                                intersect = mathutils.geometry.\
                                intersect_ray_tri(v1, v3, v4, ray, loc[1])
                                if intersect:
                                    projection = intersect
                                    break
                        if projection:
                            break
            if not projection:
                # check if projection is on adjacent edges
                for edgekey in vert_edges[loc[0]]:
                    line1 = bm_mod.verts[edgekey[0]].co
                    line2 = bm_mod.verts[edgekey[1]].co
                    intersect, dist = mathutils.geometry.intersect_point_line(
                        loc[1], line1, line2
                        )
                    if 1e-6 < dist < 1 - 1e-6:
                        projection = intersect
                        break
            if not projection:
                # full search through the entire mesh
                hits = []
                for face in faces:
                    verts = [v.co for v in face.verts]
                    if len(verts) == 3:  # triangle
                        v1, v2, v3 = verts
                        v4 = False
                    else:  # assume quad
                        v1, v2, v3, v4 = verts[:4]
                    for ray in rays:
                        intersect = mathutils.geometry.intersect_ray_tri(
                            v1, v2, v3, ray, loc[1]
                            )
                        if intersect:
                            hits.append([(loc[1] - intersect).length,
                                intersect])
                            break
                        elif v4:
                            intersect = mathutils.geometry.intersect_ray_tri(
                                v1, v3, v4, ray, loc[1]
                                )
                            if intersect:
                                hits.append([(loc[1] - intersect).length,
                                    intersect])
                                break
                if len(hits) >= 1:
                    # if more than 1 hit with mesh, closest hit is new loc
                    hits.sort()
                    projection = hits[0][1]
            if not projection:
                # nothing to project on, remain at flat location
                projection = loc[1]
            new_locs.append([loc[0], projection])

        # return new positions of projected circle
        return(new_locs)

# check loops and only return valid ones
def circle_check_loops(single_loops, loops, mapping, bm_mod):
    valid_single_loops = {}
    valid_loops = []
    for i, [loop, circular] in enumerate(loops):
        # loop needs to have at least 3 vertices
        if len(loop) < 3:
            continue
        # loop needs at least 1 vertex in the original, non-mirrored mesh
        if mapping:
            all_virtual = True
            for vert in loop:
                if mapping[vert] > -1:
                    all_virtual = False
                    break
            if all_virtual:
                continue
        # loop has to be non-collinear
        collinear = True
        loc0 = mathutils.Vector(bm_mod.verts[loop[0]].co[:])
        loc1 = mathutils.Vector(bm_mod.verts[loop[1]].co[:])
        for v in loop[2:]:
            locn = mathutils.Vector(bm_mod.verts[v].co[:])
            if loc0 == loc1 or loc1 == locn:
                loc0 = loc1
                loc1 = locn
                continue
            d1 = loc1 - loc0
            d2 = locn - loc1
            if -1e-6 < d1.angle(d2, 0) < 1e-6:
                loc0 = loc1
                loc1 = locn
                continue
            collinear = False
            break
        if collinear:
            continue
        # passed all tests, loop is valid
        valid_loops.append([loop, circular])
        valid_single_loops[len(valid_loops) - 1] = single_loops[i]

    return(valid_single_loops, valid_loops)

# return a mapping of derived indices to indices
def get_mapping(derived, bm, bm_mod, single_vertices, full_search, loops):
    if not derived:
        return(False)

    if full_search:
        verts = [v for v in bm.verts if not v.hide]
    else:
        verts = [v for v in bm.verts if v.select and not v.hide]

    # non-selected vertices around single vertices also need to be mapped
    if single_vertices:
        mapping = dict([[vert, -1] for vert in single_vertices])
        verts_mod = [bm_mod.verts[vert] for vert in single_vertices]
        for v in verts:
            for v_mod in verts_mod:
                if (v.co - v_mod.co).length < 1e-6:
                    mapping[v_mod.index] = v.index
                    break
        real_singles = [v_real for v_real in mapping.values() if v_real > -1]

        verts_indices = [vert.index for vert in verts]
        for face in [face for face in bm.faces if not face.select and not face.hide]:
            for vert in face.verts:
                if vert.index in real_singles:
                    for v in face.verts:
                        if v.index not in verts_indices:
                            if v not in verts:
                                verts.append(v)
                    break

    # create mapping of derived indices to indices
    mapping = dict([[vert, -1] for loop in loops for vert in loop[0]])
    if single_vertices:
        for single in single_vertices:
            mapping[single] = -1
    verts_mod = [bm_mod.verts[i] for i in mapping.keys()]
    for v in verts:
        for v_mod in verts_mod:
            if (v.co - v_mod.co).length < 1e-6:
                mapping[v_mod.index] = v.index
                verts_mod.remove(v_mod)
                break

    return(mapping)

# recalculate positions based on the influence of the circle shape
def circle_influence_locs(locs_2d, new_locs_2d, influence):
    for i in range(len(locs_2d)):
        oldx, oldy, j = locs_2d[i]
        newx, newy, k = new_locs_2d[i]
        altx = newx * (influence / 100) + oldx * ((100 - influence) / 100)
        alty = newy * (influence / 100) + oldy * ((100 - influence) / 100)
        locs_2d[i] = [altx, alty, j]

    return(locs_2d)

# project 2d locations on circle, respecting distance relations between verts
def circle_project_non_regular(locs_2d, x0, y0, r):
    for i in range(len(locs_2d)):
        x, y, j = locs_2d[i]
        loc = mathutils.Vector([x - x0, y - y0])
        loc.length = r
        locs_2d[i] = [loc[0], loc[1], j]

    return(locs_2d)

# project 2d locations on circle, with equal distance between all vertices
def circle_project_regular(locs_2d, x0, y0, r):
    # find offset angle and circling direction
    x, y, i = locs_2d[0]
    loc = mathutils.Vector([x - x0, y - y0])
    loc.length = r
    offset_angle = loc.angle(mathutils.Vector([1.0, 0.0]), 0.0)
    loca = mathutils.Vector([x - x0, y - y0, 0.0])
    if loc[1] < -1e-6:
        offset_angle *= -1
    x, y, j = locs_2d[1]
    locb = mathutils.Vector([x - x0, y - y0, 0.0])
    if loca.cross(locb)[2] >= 0:
        ccw = 1
    else:
        ccw = -1
    # distribute vertices along the circle
    for i in range(len(locs_2d)):
        t = offset_angle + ccw * (i / len(locs_2d) * 2 * math.pi)
        x = math.cos(t) * r
        y = math.sin(t) * r
        locs_2d[i] = [x, y, locs_2d[i][2]]

    return(locs_2d)

# calculate the location of single input vertices that need to be flattened
def circle_flatten_singles(bm_mod, com, p, q, normal, single_loop):
    new_locs = []
    for vert in single_loop:
        loc = mathutils.Vector(bm_mod.verts[vert].co[:])
        new_locs.append([vert, loc - (loc - com).dot(normal) * normal])

    return(new_locs)



class Mesh_OT_Flatten(Operator):                                #-----------------------------------------------------------------------------------------------
    bl_idname = "mesh.flatten"
    bl_label = "Flatten"
    bl_description = "Flatten vertices on a best-fitting plane"
    bl_options = {'REGISTER', 'UNDO'}

    influence: FloatProperty(
        name="Influence",
        description="Force of the tool",
        default=100.0,
        min=0.0,
        max=100.0,
        precision=1,
        subtype='PERCENTAGE'
        )
    lock_x: BoolProperty(
        name="Lock X",
        description="Lock editing of the x-coordinate",
        default=False
        )
    lock_y: BoolProperty(
        name="Lock Y",
        description="Lock editing of the y-coordinate",
        default=False
        )
    lock_z: BoolProperty(name="Lock Z",
        description="Lock editing of the z-coordinate",
        default=False
        )
    plane: EnumProperty(
        name="Plane",
        items=(("best_fit", "Best fit", "Calculate a best fitting plane"),
              ("normal", "Normal", "Derive plane from averaging vertex normals"),
              ("view", "View", "Flatten on a plane perpendicular to the viewing angle")),
        description="Plane on which vertices are flattened",
        default='best_fit'
        )
    restriction: EnumProperty(
        name="Restriction",
        items=(("none", "None", "No restrictions on vertex movement"),
               ("bounding_box", "Bounding box", "Vertices are restricted to "
               "movement inside the bounding box of the selection")),
        description="Restrictions on how the vertices can be moved",
        default='none'
        )

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "plane")
        # col.prop(self, "restriction")
        col.separator()

        col_move = col.column(align=True)
        row = col_move.row(align=True)
        if self.lock_x:
            row.prop(self, "lock_x", text="X", icon='LOCKED')
        else:
            row.prop(self, "lock_x", text="X", icon='UNLOCKED')
        if self.lock_y:
            row.prop(self, "lock_y", text="Y", icon='LOCKED')
        else:
            row.prop(self, "lock_y", text="Y", icon='UNLOCKED')
        if self.lock_z:
            row.prop(self, "lock_z", text="Z", icon='LOCKED')
        else:
            row.prop(self, "lock_z", text="Z", icon='UNLOCKED')
        col_move.prop(self, "influence")

    # def invoke(self, context, event):
    #     # load custom settings
    #     settings_load(self)
    #     return self.execute(context)

    def execute(self, context):
        # initialise
        object, bm = initialise()
        # settings_write(self)
        # check cache to see if we can save time
        cached, single_loops, loops, derived, mapping = cache_read("Flatten",
            object, bm, False, False)
        if not cached:
            # order input into virtual loops
            loops = flatten_get_input(bm)
            loops = check_loops(loops, mapping, bm)

        # saving cache for faster execution next time
        if not cached:
            cache_write("Flatten", object, bm, False, False, False, loops,
                False, False)

        move = []
        for loop in loops:
            # calculate plane and position of vertices on them
            com, normal = calculate_plane(bm, loop, method=self.plane,
                object=object)
            to_move = flatten_project(bm, loop, com, normal)
            if self.restriction == 'none':
                move.append(to_move)
            else:
                move.append(to_move)

        # move vertices to new locations
        if self.lock_x or self.lock_y or self.lock_z:
            lock = [self.lock_x, self.lock_y, self.lock_z]
        else:
            lock = False
        move_verts(object, bm, False, move, lock, self.influence)

        # cleaning up
        terminate()

        return{'FINISHED'}


# circle operator
class Mesh_OT_Circle(Operator):
    bl_idname = "mesh.circle"
    bl_label = "Circle"
    bl_description = "Move selected vertices into a circle shape"
    bl_options = {'REGISTER', 'UNDO'}

    custom_radius: BoolProperty(
        name="Radius",
        description="Force a custom radius",
        default=False
        )
    fit: EnumProperty(
        name="Method",
        items=(("best", "Best fit", "Non-linear least squares"),
               ("inside", "Fit inside", "Only move vertices towards the center")),
        description="Method used for fitting a circle to the vertices",
        default='best'
        )
    flatten: BoolProperty(
        name="Flatten",
        description="Flatten the circle, instead of projecting it on the mesh",
        default=True
        )
    influence: FloatProperty(
        name="Influence",
        description="Force of the tool",
        default=100.0,
        min=0.0,
        max=100.0,
        precision=1,
        subtype='PERCENTAGE'
        )
    lock_x: BoolProperty(
        name="Lock X",
        description="Lock editing of the x-coordinate",
        default=False
        )
    lock_y: BoolProperty(
        name="Lock Y",
        description="Lock editing of the y-coordinate",
        default=False
        )
    lock_z: BoolProperty(name="Lock Z",
        description="Lock editing of the z-coordinate",
        default=False
        )
    radius: FloatProperty(
        name="Radius",
        description="Custom radius for circle",
        default=1.0,
        min=0.0,
        soft_max=1000.0
        )
    regular: BoolProperty(
        name="Regular",
        description="Distribute vertices at constant distances along the circle",
        default=True
        )

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.prop(self, "fit")
        col.separator()

        col.prop(self, "flatten")
        row = col.row(align=True)
        row.prop(self, "custom_radius")
        row_right = row.row(align=True)
        row_right.active = self.custom_radius
        row_right.prop(self, "radius", text="")
        col.prop(self, "regular")
        col.separator()

        col_move = col.column(align=True)
        row = col_move.row(align=True)
        if self.lock_x:
            row.prop(self, "lock_x", text="X", icon='LOCKED')
        else:
            row.prop(self, "lock_x", text="X", icon='UNLOCKED')
        if self.lock_y:
            row.prop(self, "lock_y", text="Y", icon='LOCKED')
        else:
            row.prop(self, "lock_y", text="Y", icon='UNLOCKED')
        if self.lock_z:
            row.prop(self, "lock_z", text="Z", icon='LOCKED')
        else:
            row.prop(self, "lock_z", text="Z", icon='UNLOCKED')
        col_move.prop(self, "influence")

    # def invoke(self, context, event):
    #     # load custom settings
    #     # settings_load(self)
    #     return self.execute(context)

    def execute(self, context):
        # initialise
        object, bm = initialise()
        # settings_write(self)
        # check cache to see if we can save time
        cached, single_loops, loops, derived, mapping = cache_read("Circle",
            object, bm, False, False)
        if cached:
            derived, bm_mod = get_derived_bmesh(object, bm, False)
        else:
            # find loops
            derived, bm_mod, single_vertices, single_loops, loops = \
                circle_get_input(object, bm)
            mapping = get_mapping(derived, bm, bm_mod, single_vertices,
                False, loops)
            single_loops, loops = circle_check_loops(single_loops, loops,
                mapping, bm_mod)

        # saving cache for faster execution next time
        if not cached:
            cache_write("Circle", object, bm, False, False, single_loops,
                loops, derived, mapping)

        move = []
        for i, loop in enumerate(loops):
            # best fitting flat plane
            com, normal = calculate_plane(bm_mod, loop)
            # if circular, shift loop so we get a good starting vertex
            if loop[1]:
                loop = circle_shift_loop(bm_mod, loop, com)
            # flatten vertices on plane
            locs_2d, p, q = circle_3d_to_2d(bm_mod, loop, com, normal)
            # calculate circle
            if self.fit == 'best':
                x0, y0, r = circle_calculate_best_fit(locs_2d)
            else:  # self.fit == 'inside'
                x0, y0, r = circle_calculate_min_fit(locs_2d)
            # radius override
            if self.custom_radius:
                r = self.radius / p.length
            # calculate positions on circle
            if self.regular:
                new_locs_2d = circle_project_regular(locs_2d[:], x0, y0, r)
            else:
                new_locs_2d = circle_project_non_regular(locs_2d[:], x0, y0, r)
            # take influence into account
            locs_2d = circle_influence_locs(locs_2d, new_locs_2d,
                self.influence)
            # calculate 3d positions of the created 2d input
            move.append(circle_calculate_verts(self.flatten, bm_mod,
                locs_2d, com, p, q, normal))
            # flatten single input vertices on plane defined by loop
            if self.flatten and single_loops:
                move.append(circle_flatten_singles(bm_mod, com, p, q,
                    normal, single_loops[i]))

        # move vertices to new locations
        if self.lock_x or self.lock_y or self.lock_z:
            lock = [self.lock_x, self.lock_y, self.lock_z]
        else:
            lock = False
        move_verts(object, bm, mapping, move, lock, -1)

        # cleaning up
        if derived:
            bm_mod.free()
        terminate()

        return{'FINISHED'}



classes = [

    Mesh_OT_Flatten,
    Mesh_OT_Circle,

]


def register():
    
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():   
    
     for cls in classes:
        bpy.utils.unregister_class(cls)
