"""Shared helpers for the Blender scenes in art/ (clay-miniature look)."""
import math

import bpy
from mathutils import Matrix, Vector


def clear():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    return bpy.context.scene


def mat(name, color, rough=0.55, sss=0.0, emit=None, strength=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (0.3, 0.15, 0.1)
        p.inputs["Subsurface Scale"].default_value = 0.05
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = strength
    if coat:
        p.inputs["Coat Weight"].default_value = coat
    return m


def wood(m, scale=1.2):
    nt = m.node_tree
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.inputs["Scale"].default_value = scale
    wave.inputs["Distortion"].default_value = 6
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.42, 0.22, 0.11, 1)
    ramp.color_ramp.elements[1].color = (0.66, 0.40, 0.22, 1)
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])


def smooth(ob):
    for poly in ob.data.polygons:
        poly.use_smooth = True


def rbox(name, size, loc, m, bevel=0.2, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    md = ob.modifiers.new("bev", "BEVEL")
    md.width = bevel
    md.segments = 10
    md.limit_method = "NONE"
    smooth(ob)
    ob.data.materials.append(m)
    return ob


def ball(name, loc, scale, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    smooth(ob)
    ob.data.materials.append(m)
    return ob


def tube(name, pts, radius, m, caps=True, smooth_path=False):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 6
    cu.use_fill_caps = caps
    if smooth_path:
        sp = cu.splines.new("NURBS")
        sp.order_u = min(4, len(pts))
        sp.use_endpoint_u = True
        cu.resolution_u = 24
    else:
        sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(m)
    return ob


def arc(cx, cz, r, a0, a1, y, n=24):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), y, cz + r * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


def heart_pts(cx, cz, s, y, n=60):
    """A closed heart outline in the XZ plane (facing -Y)."""
    pts = []
    for i in range(n + 1):
        t = i / n * 2 * math.pi
        hx = 16 * math.sin(t) ** 3
        hz = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + hx * s, y, cz + hz * s))
    return pts


def heart_solid(name, loc, s, depth, m, rot=(math.pi / 2, 0, 0)):
    """A filled, extruded heart (curve with fill), standing up and facing -Y."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = depth
    sp = cu.splines.new("POLY")
    n = 60
    sp.points.add(n - 1)
    for i in range(n):
        t = i / n * 2 * math.pi
        hx = 16 * math.sin(t) ** 3
        hy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        sp.points[i].co = (hx * s, hy * s, 0, 1)
    sp.use_cyclic_u = True
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    ob.data.materials.append(m)
    return ob


def text(name, body, loc, size, m, font, rot=(math.pi / 2, 0, 0), extrude=0.0):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.font = bpy.data.fonts.load(font)
    cu.size = size
    cu.space_line = 0.8
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = extrude
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    ob.data.materials.append(m)
    return ob


def pivot(loc):
    """An empty to hang a group of parts on; rotate it only after parent_all."""
    bpy.ops.object.empty_add(location=loc)
    return bpy.context.object


def parent_all(parts, parent):
    """Parent parts keeping their place; call while the pivot is unrotated."""
    bpy.context.view_layer.update()
    inv = parent.matrix_world.inverted()
    for p in parts:
        p.parent = parent
        p.matrix_parent_inverse = inv
    parent["inv"] = [list(r) for r in inv]


def world_point(parent, p):
    """Where a point given in the scene's build coordinates ends up once the
    pivot is rotated (the same transform its parented parts get)."""
    bpy.context.view_layer.update()
    inv = Matrix(parent["inv"])
    return parent.matrix_world @ inv @ Vector(p)


def light(name, kind, loc, energy, color, size=1.0, target=(0, 0, 1.2), spot_deg=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == "AREA":
        ld.size = size
    if kind == "SPOT" and spot_deg:
        ld.spot_size = math.radians(spot_deg)
        ld.spot_blend = 1.0
    if kind in ("POINT", "SPOT"):
        ld.shadow_soft_size = size
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    bpy.context.scene.collection.objects.link(lo)
    d = Vector(target) - Vector(loc)
    lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return lo


def camera(loc, aim, focus, lens=50, fstop=0.6):
    scene = bpy.context.scene
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.dof.use_dof = True
    cam = bpy.data.objects.new("cam", cd)
    scene.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(aim) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.dof.focus_distance = (Vector(focus) - cam.location).length
    cd.dof.aperture_fstop = fstop
    scene.camera = cam
    return cam


def world(color=(0.9, 0.6, 0.4), strength=0.25):
    w = bpy.data.worlds.new("w")
    bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (*color, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = strength


def render(out, res, samples, look="AgX - Punchy"):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = look
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
