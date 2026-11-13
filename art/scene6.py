"""Blender scene 6 (dev-time only): hanging up the sun.

  blender -b --factory-startup -P art/scene6.py -- OUT.png [RES] [SAMPLES]

Dawn. At the top of a very tall stepladder a tiny robot hooks the morning
sun's string onto a little cloud; the huge sun beams.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clay as C  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "//render6.png"
RES = int(argv[1]) if len(argv) > 1 else 1024
SAMPLES = int(argv[2]) if len(argv) > 2 else 256
R = math.radians
rng = random.Random(5)

scene = C.clear()

M = {"clay": C.mat("clay", (0.93, 0.80, 0.62), 0.6, sss=0.15),
     "mint": C.mat("mint", (0.55, 0.82, 0.74), 0.55, sss=0.1),
     "screen": C.mat("screen", (0.02, 0.03, 0.05), 0.18, coat=0.6),
     "glow": C.mat("glow", (0.5, 1.0, 0.85), 0.5, emit=(0.45, 1.0, 0.8), strength=6),
     "blush": C.mat("blush", (1.0, 0.45, 0.55), 0.5, emit=(1.0, 0.35, 0.45), strength=2.5)}
SUN = C.mat("sun", (1.0, 0.55, 0.03), 0.55, sss=0.15, emit=(1.0, 0.45, 0.02), strength=1.1)
RAY = C.mat("ray", (1.0, 0.38, 0.02), 0.55, emit=(1.0, 0.32, 0.01), strength=1.5)
SUNFACE = C.mat("sunface", (0.45, 0.14, 0.03), 0.5)
SUNMOUTH = C.mat("sunmouth", (0.55, 0.12, 0.06), 0.5)
SUNTONGUE = C.mat("suntongue", (1.0, 0.4, 0.35), 0.5)
SUNCHEEK = C.mat("suncheek", (1.0, 0.38, 0.25), 0.5)
CLOUD = C.mat("cloud", (1.0, 0.97, 0.95), 0.7, sss=0.6)
LADDER = C.mat("ladder", (0.78, 0.5, 0.28), 0.6)
STRING = C.mat("string", (0.55, 0.35, 0.25), 0.8)
GRASS = C.mat("grass", (0.5, 0.78, 0.25), 0.8)
GRASS2 = C.mat("grass2", (0.4, 0.66, 0.28), 0.8)
METAL = C.mat("metal", (0.75, 0.72, 0.7), 0.3)

# ---------------------------------------------------------------- dawn sky backdrop
sky = bpy.data.materials.new("sky")
sky.use_nodes = True
nt = sky.node_tree
nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.38
ramp.color_ramp.elements[0].color = (1.0, 0.62, 0.3, 1)
ramp.color_ramp.elements[1].position = 0.75
ramp.color_ramp.elements[1].color = (0.45, 0.68, 1.0, 1)
mid = ramp.color_ramp.elements.new(0.52)
mid.color = (1.0, 0.72, 0.68, 1)
em = nt.nodes.new("ShaderNodeEmission")
em.inputs["Strength"].default_value = 2.2
out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 25, 4), rotation=(math.pi / 2, 0, 0))
bk = bpy.context.object
bk.scale = (60, 40, 1)
bk.data.materials.append(sky)

# rolling hills
C.ball("hill", (0, 6, -30.0), (45, 30, 30.2), GRASS)
C.ball("hill2", (-9, 14, -6.5), (10, 4, 7.6), GRASS2)
C.ball("hill3", (10, 15, -7.2), (12, 4, 8.2), GRASS2)

# ---------------------------------------------------------------- the sun, hanging on a string
SC = Vector((-0.35, 0.6, 3.05))
SR = 1.45
sp = [C.ball("sun", tuple(SC), (SR, SR * 0.92, SR), SUN)]
for k in range(16):
    a = k * 2 * math.pi / 16 + 0.1
    d = Vector((math.cos(a), 0, math.sin(a)))
    base = SC + d * (SR * 0.95) + Vector((0, 0.15, 0))
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.26, radius2=0.04, depth=0.55, location=tuple(base + d * 0.24))
    ray = bpy.context.object
    ray.rotation_euler = (0, math.atan2(d.x, d.z), 0)
    md = ray.modifiers.new("bev", "BEVEL")
    md.width, md.segments, md.limit_method = 0.04, 6, "NONE"
    C.smooth(ray)
    ray.data.materials.append(RAY)


def on_sun(x, z, lift=0.0):
    dy = math.sqrt(max(0.0, SR * SR - x * x - z * z)) * 0.92
    return (SC.x + x, SC.y - dy - lift, SC.z + z)


for ex in (-0.46, 0.46):
    pts = [on_sun(ex + 0.22 * math.cos(t), 0.2 + 0.19 * math.sin(t)) for t in
           [0.2 + (math.pi - 0.4) * i / 20 for i in range(21)]]
    C.tube("suneye", pts, 0.05, SUNFACE)
    C.ball("suncheek", on_sun(ex * 1.5, -0.15, -0.02), (0.17, 0.06, 0.1), SUNCHEEK)
C.flat_solid("sunmouth", C.grin_pts(0.34, 0.34), on_sun(0, -0.1, 0.03), 0.06, SUNMOUTH)
C.ball("suntongue", on_sun(0, -0.36), (0.16, 0.06, 0.08), SUNTONGUE)

# the little cloud with a hook, and the string up to it
CL = Vector((1.05, 0.5, 5.25))
for (dx, dz, r) in ((0, 0, 0.42), (-0.45, -0.08, 0.32), (0.45, -0.1, 0.3), (-0.2, 0.22, 0.3), (0.25, 0.2, 0.28),
                    (-0.8, -0.15, 0.22), (0.8, -0.16, 0.2)):
    C.ball("cloud", tuple(CL + Vector((dx, 0, dz))), (r, r * 0.8, r * 0.85), CLOUD)
hook = CL + Vector((0.0, -0.1, -0.52))
C.tube("hookstem", [tuple(CL + Vector((0, -0.1, -0.2))), tuple(hook + Vector((0, 0, 0.05)))], 0.02, METAL)
C.tube("hook", C.arc(hook.x - 0.07, hook.z + 0.0, 0.07, 0.0, -math.pi * 1.1, hook.y), 0.02, METAL)
sun_top = Vector(on_sun(0.55, SR * 0.8, -0.05)) + Vector((0, 0.2, 0.05))
C.tube("sunstring", [tuple(sun_top), tuple(hook + Vector((-0.07, 0, -0.08)))], 0.015, STRING)

# a few small clouds far off
for (x, z, s) in ((-3.4, 5.4, 0.9), (3.6, 4.2, 0.7), (-3.9, 2.6, 0.6)):
    for k in range(4):
        C.ball("farcloud", (x + (k - 1.5) * 0.35 * s, 3, z + (0.12 if k in (1, 2) else 0) * s),
               (0.32 * s, 0.25 * s, 0.25 * s), CLOUD)

# ---------------------------------------------------------------- the stepladder
LX, LT = 1.75, 3.85  # x of the ladder, height of its top step
for side in (-1, 1):
    C.tube("front_rail", [(LX + side * 0.3, -0.55, 0.0), (LX + side * 0.24, -0.05, LT)], 0.04, LADDER, caps=True)
    C.tube("back_rail", [(LX + side * 0.3, 0.75, 0.0), (LX + side * 0.24, 0.15, LT)], 0.04, LADDER, caps=True)
for k in range(1, 11):
    t = k / 11
    zz = LT * t
    yy = -0.55 + 0.5 * t
    hw = 0.3 - 0.06 * t
    C.tube("rung", [(LX - hw, yy, zz), (LX + hw, yy, zz)], 0.03, LADDER)
C.rbox("top", (0.66, 0.42, 0.07), (LX, 0.05, LT + 0.03), LADDER, 0.02)

# ---------------------------------------------------------------- the tiny robot on top
S = 0.42
rb = C.robot((LX, 0.0, LT + 0.07), S, M, head_rot=(R(-12), R(-10), R(-14)))
# left hand at the hook (hanging the loop), right arm out for balance, waving
hand_l = hook + Vector((0.02, -0.05, -0.04))
C.arm(rb["l_shoulder"], hand_l, S, M["mint"], M["clay"], bend=(0.1, -0.2, 0.25))
C.arm(rb["r_shoulder"], rb["r_shoulder"] + Vector((0.42, -0.1, 0.3)), S, M["mint"], M["clay"], bend=(0.1, -0.1, -0.15))

# ---------------------------------------------------------------- light, camera
C.light("key", "AREA", (-4.0, -6.0, 6.0), 3500, (1.0, 0.85, 0.7), 6.0, target=(0.5, 0, 2.5))
C.light("fill", "AREA", (5.0, -5.0, 3.0), 900, (0.85, 0.9, 1.0), 6.0, target=(1, 0, 3))
C.light("sunspill", "POINT", (1.2, -0.6, 3.4), 250, (1.0, 0.6, 0.25), size=0.6)
C.world((1.0, 0.85, 0.75), 0.4)
C.camera((0.45, -9.6, 1.5), (0.45, 0, 3.2), (1.2, 0, 3.5), lens=40, fstop=4.0)
C.render(OUT, RES, SAMPLES)
