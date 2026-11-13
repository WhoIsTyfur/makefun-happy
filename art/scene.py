"""Blender scene for the entry (dev-time only).

Run headless:
  blender -b --factory-startup -P art/scene.py -- OUT.png [RES] [SAMPLES]

A small clay robot holds a daisy out toward the camera: the viewer, who is
the judge. Clay-miniature look: soft warm key light, depth of field and
fairy-light bokeh behind.
"""
import math
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "//render.png"
RES = int(argv[1]) if len(argv) > 1 else 1024
SAMPLES = int(argv[2]) if len(argv) > 2 else 256
FONT = "C:/Windows/Fonts/segoeprb.ttf"

# ---------------------------------------------------------------- utilities
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
scene = bpy.context.scene


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


def tube(name, pts, radius, m, caps=True):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 6
    cu.use_fill_caps = caps
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    ob = bpy.data.objects.new(name, cu)
    scene.collection.objects.link(ob)
    ob.data.materials.append(m)
    return ob


def arc(cx, cz, r, a0, a1, y, n=24):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), y, cz + r * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


# ---------------------------------------------------------------- materials
CLAY = mat("clay", (0.93, 0.80, 0.62), 0.6, sss=0.15)
MINT = mat("mint", (0.55, 0.82, 0.74), 0.55, sss=0.1)
SCREEN = mat("screen", (0.02, 0.03, 0.05), 0.18, coat=0.6)
GLOW = mat("glow", (0.5, 1.0, 0.85), 0.5, emit=(0.45, 1.0, 0.8), strength=6)
BLUSH = mat("blush", (1.0, 0.45, 0.55), 0.5, emit=(1.0, 0.35, 0.45), strength=2.5)
PETAL = mat("petal", (0.97, 0.96, 0.92), 0.5, sss=0.4)
CENTER = mat("center", (1.0, 0.7, 0.08), 0.6)
STEM = mat("stem", (0.25, 0.55, 0.2), 0.6)
WOOD = mat("wood", (0.55, 0.32, 0.17), 0.45)
PAPER = mat("paper", (0.98, 0.94, 0.86), 0.7)
INK = mat("ink", (0.45, 0.03, 0.08), 0.6)
WALL = mat("wall", (0.95, 0.62, 0.42), 0.9)
BULB = mat("bulb", (1, 0.7, 0.4), 0.5, emit=(1.0, 0.55, 0.2), strength=14)

# wood grain on the table
nt = WOOD.node_tree
wave = nt.nodes.new("ShaderNodeTexWave")
wave.inputs["Scale"].default_value = 1.2
wave.inputs["Distortion"].default_value = 6
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.42, 0.22, 0.11, 1)
ramp.color_ramp.elements[1].color = (0.66, 0.40, 0.22, 1)
nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])

# ---------------------------------------------------------------- set
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 4, 0))
bpy.context.object.data.materials.append(WOOD)
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 7, 0), rotation=(math.pi / 2, 0, 0))
bpy.context.object.data.materials.append(WALL)
# fairy lights strung behind: they turn into warm bokeh
for i in range(26):
    x = -4.2 + i * 0.34
    z = 2.9 + 0.55 * math.cos((x + 0.3) * 0.9) - 0.15 * math.sin(i * 1.7)
    ball(f"bulb{i}", (x, 6.2, z), (0.07, 0.07, 0.07), BULB)

# ---------------------------------------------------------------- robot
TILT = math.radians(-8)  # head tilts a little, shy
rbox("leg_l", (0.22, 0.24, 0.3), (-0.22, 0, 0.15), MINT, 0.1)
rbox("leg_r", (0.22, 0.24, 0.3), (0.22, 0, 0.15), MINT, 0.1)
rbox("body", (0.95, 0.72, 0.78), (0, 0, 0.68), CLAY, 0.28)
ball("chest_heart_l", (-0.06, -0.37, 0.75), (0.07, 0.03, 0.07), BLUSH)
ball("chest_heart_r", (0.06, -0.37, 0.75), (0.07, 0.03, 0.07), BLUSH)
ball("chest_heart_b", (0.0, -0.37, 0.68), (0.06, 0.03, 0.06), BLUSH, rot=(0, math.radians(45), 0))
bpy.ops.object.empty_add(location=(0, 0, 1.08))
neck = bpy.context.object
neck.rotation_euler = (0, TILT, 0)
head_parts = []
head_parts.append(rbox("head", (1.3, 0.95, 1.0), (0, 0, 1.6), CLAY, 0.34))
head_parts.append(rbox("screen", (1.0, 0.1, 0.68), (0, -0.45, 1.6), SCREEN, 0.18))
# happy closed eyes (upside-down U arcs), smile, blush
for ex in (-0.22, 0.22):
    head_parts.append(tube("eye", arc(ex, 1.6, 0.11, 0.15, math.pi - 0.15, -0.515), 0.028, GLOW))
head_parts.append(tube("smile", arc(0, 1.53, 0.13, math.pi + 0.5, 2 * math.pi - 0.5, -0.515), 0.024, GLOW))
for bx in (-0.36, 0.36):
    head_parts.append(ball("blush", (bx, -0.5, 1.47), (0.08, 0.012, 0.05), BLUSH))
head_parts.append(tube("antenna", [(0, 0, 2.1), (0.03, 0, 2.32)], 0.025, MINT))
head_parts.append(ball("antenna_bulb", (0.03, 0, 2.36), (0.07, 0.07, 0.07), BULB))
for side in (-1, 1):
    head_parts.append(ball("ear", (side * 0.68, 0, 1.6), (0.07, 0.17, 0.17), MINT))
for p in head_parts:
    p.parent = neck
    p.matrix_parent_inverse = neck.matrix_world.inverted()

# offering arm (viewer's right) reaches toward the camera; the other hides behind
hand = Vector((0.72, -1.05, 1.05))
tube("arm_r", [(0.42, -0.05, 0.85), (0.62, -0.5, 0.95), tuple(hand)], 0.085, MINT)
ball("hand_r", tuple(hand), (0.12, 0.12, 0.12), CLAY)
tube("arm_l", [(-0.45, 0.0, 0.85), (-0.55, 0.25, 0.65), (-0.3, 0.42, 0.55)], 0.085, MINT)

# ---------------------------------------------------------------- daisy
bloom = Vector((0.98, -1.35, 1.62))
tube("stem", [tuple(hand + Vector((0, 0, -0.12))), tuple(hand + Vector((0.06, -0.1, 0.25))),
              tuple(bloom + Vector((0, 0.03, -0.05)))], 0.022, STEM)
ball("leaf", tuple(hand + Vector((-0.1, -0.08, 0.28))), (0.06, 0.015, 0.14), STEM,
     rot=(0, math.radians(35), 0))
bpy.ops.object.empty_add(location=tuple(bloom))
fl = bpy.context.object
fl.rotation_euler = (math.radians(-12), 0, math.radians(-18))
parts = [ball("center", (0, 0, 0), (0.085, 0.04, 0.085), CENTER)]
for i in range(16):
    a = i * 2 * math.pi / 16
    r = 0.17
    parts.append(ball("petal", (r * math.cos(a), 0.012 * (i % 2), r * math.sin(a)),
                      (0.12, 0.012, 0.045), PETAL, rot=(0, -a, 0)))
for p in parts:
    p.parent = fl

# paper tag on a thread, hanging from the stem below the bloom
tag_top = hand + Vector((-0.02, -0.08, 0.16))
tube("thread", [tuple(tag_top), tuple(tag_top + Vector((0.0, -0.02, -0.2)))], 0.005, INK)
tag = rbox("tag", (0.62, 0.02, 0.36), tuple(tag_top + Vector((0.0, -0.03, -0.38))), PAPER, 0.008,
           rot=(0, math.radians(-6), 0))
txt = bpy.data.curves.new("tagtext", "FONT")
txt.body = "for you,\njudge"
txt.font = bpy.data.fonts.load(FONT)
txt.size = 0.15
txt.space_line = 0.8
txt.align_x = "CENTER"
txt.align_y = "CENTER"
tob = bpy.data.objects.new("tagtext", txt)
scene.collection.objects.link(tob)
tob.location = tag.location + Vector((0, -0.016, 0))
tob.rotation_euler = (math.pi / 2, math.radians(-6), 0)
tob.data.materials.append(INK)

# ---------------------------------------------------------------- light
def light(name, kind, loc, energy, color, size=1.0, target=(0, 0, 1.2)):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == "AREA":
        ld.size = size
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    scene.collection.objects.link(lo)
    d = Vector(target) - Vector(loc)
    lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return lo


light("key", "AREA", (-3.5, -2.5, 3.6), 1300, (1.0, 0.78, 0.55), 2.5)
light("fill", "AREA", (3.5, -3.5, 1.8), 160, (0.85, 0.9, 1.0), 4.0)
light("wallglow", "SPOT", (0.0, 1.5, 4.5), 2500, (1.0, 0.62, 0.32), target=(0.3, 7, 1.8))
light("rim", "AREA", (1.5, 3.0, 3.5), 500, (1.0, 0.7, 0.45), 2.0)

world = bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.9, 0.6, 0.4, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25

# ---------------------------------------------------------------- camera
cd = bpy.data.cameras.new("cam")
cd.lens = 50
cd.dof.use_dof = True
cam = bpy.data.objects.new("cam", cd)
scene.collection.objects.link(cam)
cam.location = (0.45, -4.3, 1.35)
aim = Vector((0.3, 0, 1.22)) - cam.location
cam.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
focus = Vector((0.35, -0.6, 1.55))
cd.dof.focus_distance = (focus - cam.location).length
cd.dof.aperture_fstop = 0.6
scene.camera = cam

# ---------------------------------------------------------------- render
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = SAMPLES
scene.cycles.use_denoising = True
scene.render.resolution_x = RES
scene.render.resolution_y = RES
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Punchy"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
