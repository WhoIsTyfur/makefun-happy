"""Blender scene 5 (dev-time only): bath time for the sun.

  blender -b --factory-startup -P art/scene5.py -- OUT.png [RES] [SAMPLES]

A giant giggling sun sits in a clawfoot tub with a foam shampoo hat; the
little robot stands on a step stool scrubbing its cheek. A rubber duck rides
the foam and soap bubbles drift up.
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
OUT = argv[0] if argv else "//render5.png"
RES = int(argv[1]) if len(argv) > 1 else 1024
SAMPLES = int(argv[2]) if len(argv) > 2 else 256
MOOD = argv[3] if len(argv) > 3 else "day"  # "glow": the sun is the room's lamp
GL = MOOD == "glow"
R = math.radians
rng = random.Random(11)

scene = C.clear()

# ---------------------------------------------------------------- materials
CLAY = C.mat("clay", (0.93, 0.80, 0.62), 0.6, sss=0.15)
MINT = C.mat("mint", (0.55, 0.82, 0.74), 0.55, sss=0.1)
SCREEN = C.mat("screen", (0.02, 0.03, 0.05), 0.18, coat=0.6)
GLOW = C.mat("glow", (0.5, 1.0, 0.85), 0.5, emit=(0.45, 1.0, 0.8), strength=6)
BLUSH = C.mat("blush", (1.0, 0.45, 0.55), 0.5, emit=(1.0, 0.35, 0.45), strength=2.5)
SUN = C.mat("sun", (1.0, 0.55, 0.03), 0.55, sss=0.15, emit=(1.0, 0.4, 0.0), strength=1.8 if GL else 0.9)
RAY = C.mat("ray", (1.0, 0.38, 0.02), 0.55, emit=(1.0, 0.3, 0.0), strength=2.6 if GL else 1.2)
SUNFACE = C.mat("sunface", (0.45, 0.14, 0.03), 0.5)
SUNMOUTH = C.mat("sunmouth", (0.55, 0.12, 0.06), 0.5)
SUNTONGUE = C.mat("suntongue", (1.0, 0.4, 0.35), 0.5)
SUNCHEEK = C.mat("suncheek", (1.0, 0.38, 0.25), 0.5)
TUB = C.mat("tub", (0.97, 0.96, 0.93), 0.2, coat=0.7)
GOLD = C.mat("gold", (1.0, 0.75, 0.3), 0.3)
FOAM = C.mat("foam", (1.0, 0.99, 0.97), 0.6, sss=0.5)
DUCK = C.mat("duck", (1.0, 0.82, 0.05), 0.35, coat=0.6)
BEAK = C.mat("beak", (1.0, 0.45, 0.05), 0.4)
DARK = C.mat("dark", (0.05, 0.03, 0.02), 0.3)
BRUSH = C.mat("brush", (0.95, 0.4, 0.5), 0.5)
BRISTLE = C.mat("bristle", (0.98, 0.9, 0.7), 0.7)
STOOL = C.mat("stool", (0.45, 0.62, 0.85), 0.5)
TILE = C.mat("tile", (0.45, 0.5, 0.72) if GL else (0.95, 0.66, 0.52), 0.6)
FLOOR = C.mat("floor", (0.93, 0.78, 0.66), 0.5)

bub = bpy.data.materials.new("bubble")
bub.use_nodes = True
bp = bub.node_tree.nodes["Principled BSDF"]
bp.inputs["Base Color"].default_value = (1, 1, 1, 1)
bp.inputs["Roughness"].default_value = 0.0
bp.inputs["Transmission Weight"].default_value = 1.0
bp.inputs["IOR"].default_value = 1.05
bp.inputs["Coat Weight"].default_value = 0.3
bp.inputs["Thin Film Thickness"].default_value = 450.0

# ---------------------------------------------------------------- bathroom
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 4, 0))
bpy.context.object.data.materials.append(FLOOR)
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 4.5, 0), rotation=(math.pi / 2, 0, 0))
bpy.context.object.data.materials.append(TILE)
# tile grout: brick texture would do, but plain soft teal reads better small

# ---------------------------------------------------------------- tub
TX, TY = -0.55, 0.45
tub = C.rbox("tub", (3.7, 2.1, 1.05), (TX, TY, 0.78), TUB, 0.45)
C.rbox("rim", (3.82, 2.22, 0.12), (TX, TY, 1.28), TUB, 0.06)
for fx in (-1.55, 1.55):
    for fy in (-0.7, 0.7):
        C.ball("claw", (TX + fx, TY + fy, 0.16), (0.14, 0.14, 0.16), GOLD)

# ---------------------------------------------------------------- the sun, in the bath
SC = Vector((TX - 0.05, TY - 0.05, 2.08))
SR = 1.3
sun_p = C.pivot(tuple(SC))
sp = [C.ball("sun", tuple(SC), (SR, SR * 0.92, SR), SUN)]
for k in range(14):
    a = k * 2 * math.pi / 14 + 0.1
    d = Vector((math.cos(a), 0, math.sin(a)))
    base = SC + d * (SR * 0.95) + Vector((0, 0.15, 0))
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.26, radius2=0.04, depth=0.52,
                                    location=tuple(base + d * 0.22))
    ray = bpy.context.object
    ray.rotation_euler = (0, math.atan2(d.x, d.z), 0)
    md = ray.modifiers.new("bev", "BEVEL")
    md.width, md.segments, md.limit_method = 0.04, 6, "NONE"
    C.smooth(ray)
    ray.data.materials.append(RAY)
    sp.append(ray)


def on_sun(x, z, lift=0.0):
    """Point on the sun's front surface at offset x, z from its centre."""
    dy = math.sqrt(max(0.0, SR * SR - x * x - z * z)) * 0.92
    return (SC.x + x, SC.y - dy - lift, SC.z + z)


for ex in (-0.42, 0.42):  # blissful closed eyes
    pts = [on_sun(ex + 0.2 * math.cos(t), 0.18 + 0.17 * math.sin(t), 0.0)
           for t in [0.2 + (math.pi - 0.4) * i / 20 for i in range(21)]]
    sp.append(C.tube("suneye", pts, 0.045, SUNFACE))
    sp.append(C.ball("suncheek", on_sun(ex * 1.45, -0.12, -0.02), (0.15, 0.06, 0.09), SUNCHEEK))
mouth = C.flat_solid("sunmouth", C.grin_pts(0.3, 0.3), on_sun(0, -0.1, 0.03), 0.06, SUNMOUTH)
sp.append(mouth)
sp.append(C.ball("suntongue", on_sun(0, -0.33, -0.0), (0.14, 0.06, 0.07), SUNTONGUE))
# foam shampoo hat
for i in range(16):
    a = rng.uniform(-1.0, 1.0)
    p = SC + Vector((a * 0.65, rng.uniform(-0.3, 0.3), SR * 0.93 - abs(a) * 0.3 + rng.uniform(0.0, 0.2)))
    s = rng.uniform(0.13, 0.22)
    sp.append(C.ball("shampoo", tuple(p), (s, s, s * 0.9), FOAM))
C.parent_all(sp, sun_p)
sun_p.rotation_euler = (0, R(8), R(14))  # leans into the scrub, turning toward the robot

# foam heaped over the water line
for i in range(120):
    x = rng.uniform(-1.8, 1.8)
    y = rng.uniform(-0.95, 0.95)
    if abs(x) > 1.7 and abs(y) > 0.85:
        continue
    z = 1.32 + rng.uniform(-0.02, 0.12)
    s = rng.uniform(0.12, 0.26)
    C.ball("foam", (TX + x, TY + y, z), (s, s, s * 0.8), FOAM)
for i in range(10):  # foam spilling over the front rim
    x = rng.uniform(-1.4, 1.4)
    s = rng.uniform(0.1, 0.18)
    C.ball("spill", (TX + x, TY - 1.08, 1.26 - rng.uniform(0, 0.2)), (s, s * 0.8, s), FOAM)

# rubber duck riding the foam
DK = Vector((TX - 1.45, TY - 0.6, 1.48))
C.ball("duckbody", tuple(DK), (0.2, 0.15, 0.14), DUCK)
C.ball("duckhead", tuple(DK + Vector((0.05, -0.02, 0.18))), (0.11, 0.11, 0.11), DUCK)
C.ball("duckbeak", tuple(DK + Vector((0.16, -0.05, 0.16))), (0.07, 0.05, 0.03), BEAK)
C.ball("duckeye", tuple(DK + Vector((0.1, -0.11, 0.22))), (0.02, 0.02, 0.02), DARK)

# ---------------------------------------------------------------- robot on a step stool
RX, RY = 2.0, -0.35
C.rbox("step", (0.9, 0.7, 0.6), (RX, RY, 0.3), STOOL, 0.08)
B = 0.6
C.rbox("leg_l", (0.24, 0.26, 0.3), (RX - 0.22, RY, B + 0.15), MINT, 0.08)
C.rbox("leg_r", (0.24, 0.26, 0.3), (RX + 0.22, RY, B + 0.15), MINT, 0.08)
C.rbox("body", (0.95, 0.72, 0.78), (RX, RY, B + 0.68), CLAY, 0.28)
neck = C.pivot((RX, RY, B + 1.08))
HZ = B + 1.6
hp = [C.rbox("head", (1.3, 0.95, 1.0), (RX, RY, HZ), CLAY, 0.34),
      C.rbox("screen", (1.0, 0.1, 0.68), (RX, RY - 0.45, HZ), SCREEN, 0.18)]
SY = RY - 0.512
for ex in (-0.22, 0.22):
    hp.append(C.tube("eye", C.arc(RX + ex, HZ + 0.02, 0.11, 0.15, math.pi - 0.15, SY), 0.03, GLOW))
hp.append(C.flat_solid("grin", C.grin_pts(0.14, 0.12), (RX, SY, HZ - 0.07), 0.01, GLOW))
for bx in (-0.36, 0.36):
    hp.append(C.ball("blush", (RX + bx, RY - 0.5, HZ - 0.12), (0.08, 0.012, 0.05), BLUSH))
for side in (-1, 1):
    hp.append(C.ball("ear", (RX + side * 0.68, RY, HZ), (0.07, 0.17, 0.17), MINT))
hp.append(C.ball("foamdab", (RX - 0.25, RY - 0.35, HZ + 0.52), (0.1, 0.1, 0.08), FOAM))  # a dab of foam on its head
C.parent_all(hp, neck)
neck.rotation_euler = (0, R(-8), R(-28))  # turned toward the sun

# the scrubbing arm reaches the sun's cheek with a brush
cheek = C.world_point(sun_p, tuple(on_sun(0.82, -0.2, 0.0)))
grip = cheek + Vector((0.5, -0.3, -0.1))
C.tube("rarm", [(RX - 0.45, RY - 0.05, B + 0.95), (RX - 0.62, RY - 0.3, B + 0.88), tuple(grip)], 0.08, MINT,
       smooth_path=True)
C.ball("rhand", tuple(grip), (0.11, 0.11, 0.11), CLAY)
head_end = cheek + (grip - cheek).normalized() * 0.08
C.tube("brushhandle", [tuple(grip + (grip - cheek).normalized() * 0.15), tuple(head_end + (grip - cheek).normalized() * 0.18)],
       0.035, BRUSH)
bh = C.rbox("brushhead", (0.12, 0.26, 0.12), tuple(head_end + (grip - cheek).normalized() * 0.1), BRUSH, 0.04)
bh.rotation_euler = (0, 0, math.atan2((grip - cheek).y, (grip - cheek).x))
for i in range(6):
    s = rng.uniform(0.07, 0.11)
    C.ball("scrubfoam", tuple(cheek + Vector((rng.uniform(-0.12, 0.12), -0.05, rng.uniform(-0.15, 0.15)))), (s, s, s),
           FOAM)
# other arm up, cheering the sun on
C.tube("larm", [(RX + 0.45, RY - 0.05, B + 0.95), (RX + 0.7, RY - 0.2, B + 1.2), (RX + 0.72, RY - 0.25, B + 1.55)],
       0.08, MINT, smooth_path=True)
C.ball("lhand", (RX + 0.72, RY - 0.25, B + 1.58), (0.11, 0.11, 0.11), CLAY)

# soap bubbles drifting up
for (x, y, z, r) in ((0.9, -0.6, 2.9, 0.16), (0.3, -0.9, 3.25, 0.11), (-1.9, -0.4, 2.6, 0.13), (-2.3, -0.9, 3.1, 0.09),
                     (1.4, -0.8, 3.4, 0.08), (-0.9, -1.1, 3.4, 0.1), (2.5, -0.5, 2.7, 0.12)):
    C.ball("bubble", (x, y, z), (r, r, r), bub)

# ---------------------------------------------------------------- light, camera
if GL:
    # dusk: a faint cool fill, everything else lit by the sun in the tub
    C.light("fill", "AREA", (3.0, -5.0, 3.0), 120, (0.6, 0.7, 1.0), 5.0, target=(0.5, 0, 1.4))
    C.light("glowspill", "POINT", (-0.6, -1.7, 2.1), 1400, (1.0, 0.55, 0.2), size=1.2)
    C.world((0.25, 0.3, 0.5), 0.15)
else:
    C.light("key", "AREA", (-3.2, -4.0, 4.2), 900, (1.0, 0.85, 0.7), 3.0, target=(0, 0, 1.4))
    C.light("fill", "AREA", (4.0, -4.0, 2.2), 250, (0.9, 0.92, 1.0), 4.0, target=(0.5, 0, 1.4))
    C.light("top", "AREA", (0, 0.5, 6.0), 350, (1.0, 0.9, 0.75), 4.0, target=(0, 0.5, 0))
    # late sun through a window on the left: a warm slanted patch on the wall
    C.light("window", "SPOT", (-5.0, -2.0, 4.5), 9000, (1.0, 0.7, 0.4), size=0.05, target=(-0.5, 4.5, 2.4),
            spot_deg=22)
    C.world((0.9, 0.7, 0.5), 0.3)
C.camera((0.3, -6.6, 2.05), (0.3, 0, 1.92), (0.6, -0.4, 1.9), lens=44, fstop=1.6)
C.render(OUT, RES, SAMPLES)
