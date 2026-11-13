"""Blender scene 4 (dev-time only): tea for the robot.

  blender -b --factory-startup -P art/scene4.py -- OUT.png [RES] [SAMPLES]

The robot sits squeezed onto a tiny stool at a kid's tea party, paper crown
askew, holding a tiny cup while the kid pours. Both are laughing.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clay as C  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "//render4.png"
RES = int(argv[1]) if len(argv) > 1 else 1024
SAMPLES = int(argv[2]) if len(argv) > 2 else 256
R = math.radians

scene = C.clear()

# ---------------------------------------------------------------- materials
CLAY = C.mat("clay", (0.93, 0.80, 0.62), 0.6, sss=0.15)
MINT = C.mat("mint", (0.55, 0.82, 0.74), 0.55, sss=0.1)
SCREEN = C.mat("screen", (0.02, 0.03, 0.05), 0.18, coat=0.6)
GLOW = C.mat("glow", (0.5, 1.0, 0.85), 0.5, emit=(0.45, 1.0, 0.8), strength=6)
BLUSH = C.mat("blush", (1.0, 0.45, 0.55), 0.5, emit=(1.0, 0.35, 0.45), strength=2.5)
SKIN = C.mat("skin", (0.95, 0.70, 0.55), 0.55, sss=0.3)
CHEEK = C.mat("cheek", (1.0, 0.5, 0.5), 0.6)
HAIR = C.mat("hair", (0.28, 0.14, 0.07), 0.5)
DRESS = C.mat("dress", (0.85, 0.12, 0.1), 0.6, sss=0.05)
SOCK = C.mat("sock", (0.98, 0.95, 0.9), 0.7)
SHOE = C.mat("shoe", (0.25, 0.35, 0.75), 0.45)
EYE = C.mat("eye", (0.08, 0.04, 0.03), 0.4)
MOUTH = C.mat("mouth", (0.35, 0.06, 0.06), 0.5)
TONGUE = C.mat("tongue", (1.0, 0.45, 0.45), 0.5)
CROWN = C.mat("crown", (1.0, 0.68, 0.04), 0.6, sss=0.05)
GEM = C.mat("gem", (0.95, 0.2, 0.3), 0.5)
PINK = C.mat("pink", (0.98, 0.55, 0.65), 0.5, sss=0.05)
CHINA = C.mat("china", (0.97, 0.95, 0.92), 0.25, coat=0.5)
TEA = C.mat("tea", (0.55, 0.25, 0.08), 0.1)
COOKIE = C.mat("cookie", (0.85, 0.55, 0.25), 0.7)
STOOL = C.mat("stool", (0.45, 0.62, 0.85), 0.5)
WOOD = C.mat("wood", (0.55, 0.32, 0.17), 0.45)
C.wood(WOOD)
WALL = C.mat("wall", (0.9, 0.55, 0.36), 0.9)
BULB = C.mat("bulb", (1, 0.7, 0.4), 0.5, emit=(1.0, 0.55, 0.2), strength=14)

# ---------------------------------------------------------------- set
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 4, 0))
bpy.context.object.data.materials.append(WOOD)
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 7, 0), rotation=(math.pi / 2, 0, 0))
bpy.context.object.data.materials.append(WALL)
for i in range(26):
    x = -4.2 + i * 0.34
    z = 2.6 + 0.45 * math.cos((x + 0.3) * 0.9) - 0.12 * math.sin(i * 1.7)
    C.ball(f"bulb{i}", (x, 6.2, z), (0.07, 0.07, 0.07), BULB)


def cyl(name, r, depth, loc, m, r2=None, rot=(0, 0, 0), verts=48):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=depth, location=loc,
                                        rotation=rot)
    ob = bpy.context.object
    ob.name = name
    md = ob.modifiers.new("bev", "BEVEL")
    md.width, md.segments, md.limit_method = min(0.02, depth / 3), 4, "NONE"
    C.smooth(ob)
    ob.data.materials.append(m)
    return ob


def teacup(loc, s=1.0):
    x, y, z = loc
    cyl("cup", 0.055 * s, 0.07 * s, (x, y, z), CHINA, r2=0.07 * s)
    cyl("tea", 0.062 * s, 0.004, (x, y, z + 0.03 * s), TEA, verts=32)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.025 * s, minor_radius=0.008 * s,
                                     location=(x + 0.07 * s, y, z), rotation=(math.pi / 2, 0, 0))
    h = bpy.context.object
    h.data.materials.append(CHINA)
    C.smooth(h)


# ---------------------------------------------------------------- tea table
TX, TY = 0.05, -0.35
cyl("tabletop", 0.5, 0.06, (TX, TY, 0.6), PINK)
cyl("tableleg", 0.07, 0.6, (TX, TY, 0.3), PINK)
cyl("plate", 0.16, 0.02, (TX + 0.12, TY - 0.15, 0.645), CHINA)
for dx, dy in ((0.08, -0.12), (0.17, -0.18), (0.12, -0.08)):
    cyl("cookie", 0.05, 0.02, (TX + dx, TY + dy, 0.665), COOKIE, verts=24)
teacup((TX + 0.25, TY + 0.15, 0.665))

# ---------------------------------------------------------------- robot on a tiny stool
RX, RY = -0.78, 0.05
cyl("rstool", 0.28, 0.32, (RX, RY, 0.16), STOOL)
for side in (-1, 1):  # knees poke up and forward: the stool is far too small
    C.rbox("thigh", (0.24, 0.5, 0.22), (RX + side * 0.24, RY - 0.3, 0.45), MINT, 0.08, rot=(R(-14), 0, 0))
    C.rbox("shin", (0.22, 0.22, 0.42), (RX + side * 0.24, RY - 0.56, 0.21), MINT, 0.08)
C.rbox("body", (0.95, 0.72, 0.78), (RX, RY, 0.72), CLAY, 0.28)
for dx, dz in ((-0.06, 0.07), (0.06, 0.07)):
    C.ball("chest", (RX + dx, RY - 0.37, 0.72 + dz), (0.07, 0.03, 0.07), BLUSH)
C.ball("chest", (RX, RY - 0.37, 0.72), (0.06, 0.03, 0.06), BLUSH, rot=(0, R(45), 0))

neck = C.pivot((RX, RY, 1.1))
HZ = 1.62
hp = [C.rbox("head", (1.3, 0.95, 1.0), (RX, RY, HZ), CLAY, 0.34),
      C.rbox("screen", (1.0, 0.1, 0.68), (RX, RY - 0.45, HZ), SCREEN, 0.18)]
SY = RY - 0.512
for ex in (-0.22, 0.22):  # laughing: eyes squeezed into arcs
    hp.append(C.tube("eye", C.arc(RX + ex, HZ + 0.02, 0.11, 0.15, math.pi - 0.15, SY), 0.03, GLOW))
hp.append(C.flat_solid("grin", C.grin_pts(0.15, 0.13), (RX, SY, HZ - 0.06), 0.01, GLOW))
for bx in (-0.36, 0.36):
    hp.append(C.ball("blush", (RX + bx, RY - 0.5, HZ - 0.12), (0.08, 0.012, 0.05), BLUSH))
for side in (-1, 1):
    hp.append(C.ball("ear", (RX + side * 0.68, RY, HZ), (0.07, 0.17, 0.17), MINT))
# paper crown, a bit askew
cp = []
CZ = HZ + 0.5
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.33, depth=0.16, location=(RX, RY, CZ + 0.06))
band = bpy.context.object
band.data.materials.append(CROWN)
C.smooth(band)
band.modifiers.new("sol", "SOLIDIFY").thickness = 0.02
cp.append(band)
for k in range(7):
    a = -math.pi / 2 + (k - 3) * 0.55
    px, py = RX + 0.33 * math.cos(a), RY + 0.33 * math.sin(a)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.085, radius2=0.0, depth=0.2, location=(px, py, CZ + 0.24))
    sp = bpy.context.object
    sp.scale = (1, 0.25, 1)
    sp.rotation_euler = (0, 0, a + math.pi / 2)
    sp.data.materials.append(CROWN)
    C.smooth(sp)
    cp.append(sp)
    cp.append(C.ball("tip", (px, py, CZ + 0.35), (0.03, 0.03, 0.03), GEM))
cp.append(C.heart_solid("crown_heart", (RX, RY - 0.345, CZ + 0.06), 0.0035, 0.006, GEM))
tiltc = C.pivot((RX, RY, CZ))
C.parent_all(cp, tiltc)
tiltc.rotation_euler = (R(-6), R(-17), 0)
hp.append(tiltc)
C.parent_all(hp, neck)
neck.rotation_euler = (R(4), R(7), R(24))  # turns to the kid, head tilted with the laugh

# the cup arm: a tiny cup held delicately, pinky out
cup_at = Vector((RX + 0.62, RY - 0.55, 0.98))
C.tube("rarm", [(RX + 0.48, RY - 0.05, 0.92), (RX + 0.62, RY - 0.38, 0.8), tuple(cup_at + Vector((-0.06, 0, -0.07)))],
       0.08, MINT, smooth_path=True)
C.ball("rhand", tuple(cup_at + Vector((-0.06, 0, -0.07))), (0.1, 0.1, 0.1), CLAY)
C.ball("pinky", tuple(cup_at + Vector((0.02, -0.02, -0.16))), (0.06, 0.025, 0.025), CLAY, rot=(0, R(30), 0))
teacup(tuple(cup_at), 1.2)
# the other hand rests on a knee
C.tube("larm", [(RX - 0.48, RY - 0.05, 0.92), (RX - 0.6, RY - 0.35, 0.72), (RX - 0.28, RY - 0.5, 0.6)],
       0.08, MINT, smooth_path=True)
C.ball("lhand", (RX - 0.28, RY - 0.5, 0.6), (0.1, 0.1, 0.1), CLAY)

# ---------------------------------------------------------------- kid pouring
KX, KY, BASE = 0.82, -0.3, 0.0
kid = C.pivot((KX, KY, BASE))
kp = []
for side in (-1, 1):
    kp.append(C.tube("leg", [(KX + side * 0.09, KY, BASE + 0.08), (KX + side * 0.09, KY, BASE + 0.45)], 0.055, SOCK))
    kp.append(C.ball("shoe", (KX + side * 0.09, KY - 0.06, BASE + 0.07), (0.075, 0.11, 0.06), SHOE))
bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.33, radius2=0.17, depth=0.62, location=(KX, KY, BASE + 0.68))
dress = bpy.context.object
dress.data.materials.append(DRESS)
md = dress.modifiers.new("bev", "BEVEL")
md.width, md.segments, md.limit_method = 0.08, 8, "NONE"
C.smooth(dress)
kp.append(dress)
HK = BASE + 1.25
kp.append(C.ball("head", (KX, KY, HK), (0.3, 0.29, 0.29), SKIN))
kp.append(C.ball("hair", (KX, KY + 0.05, HK + 0.06), (0.315, 0.29, 0.28), HAIR))
kp.append(C.ball("bangs", (KX, KY - 0.12, HK + 0.2), (0.25, 0.14, 0.1), HAIR, rot=(R(-20), 0, 0)))
for side in (-1, 1):
    kp.append(C.ball("bun", (KX + side * 0.3, KY + 0.05, HK + 0.14), (0.1, 0.1, 0.1), HAIR))
for ex in (-0.1, 0.1):
    kp.append(C.tube("keye", C.arc(KX + ex, HK + 0.01, 0.045, 0.2, math.pi - 0.2, KY - 0.283), 0.012, EYE))
    kp.append(C.ball("kcheek", (KX + ex * 1.6, KY - 0.255, HK - 0.07), (0.055, 0.02, 0.035), CHEEK))
kp.append(C.flat_solid("kmouth", C.grin_pts(0.07, 0.07), (KX, KY - 0.278, HK - 0.06), 0.012, MOUTH))
kp.append(C.ball("tongue", (KX, KY - 0.283, HK - 0.11), (0.037, 0.008, 0.018), TONGUE))
C.parent_all(kp, kid)
kid.rotation_euler = (0, 0, R(-50))

# teapot held in both hands, tipped toward the robot's cup, tea pouring
pot = Vector((0.22, -0.55, 1.12))
potp = C.pivot(tuple(pot))
pp = [C.ball("pot", tuple(pot), (0.16, 0.14, 0.13), PINK),
      C.ball("lid", tuple(pot + Vector((0, 0, 0.13))), (0.07, 0.07, 0.03), PINK),
      C.ball("knob", tuple(pot + Vector((0, 0, 0.17))), (0.025, 0.025, 0.025), GEM),
      C.tube("spout", [tuple(pot + Vector((-0.12, 0, -0.02))), tuple(pot + Vector((-0.22, 0, 0.04))),
                       tuple(pot + Vector((-0.27, 0, 0.1)))], 0.025, PINK, smooth_path=True)]
bpy.ops.mesh.primitive_torus_add(major_radius=0.07, minor_radius=0.018, location=tuple(pot + Vector((0.16, 0, 0.01))),
                                 rotation=(math.pi / 2, 0, 0))
h = bpy.context.object
h.data.materials.append(PINK)
C.smooth(h)
pp.append(h)
C.parent_all(pp, potp)
potp.rotation_euler = (0, R(-28), 0)
spout_tip = C.world_point(potp, tuple(pot + Vector((-0.28, 0, 0.1))))
C.tube("stream", [tuple(spout_tip), tuple((spout_tip + cup_at) / 2 + Vector((-0.04, 0, 0.05))), tuple(cup_at + Vector((0, 0, 0.03)))],
       0.02, TEA, smooth_path=True)
for side, local in ((-1, (0.03, -0.12, -0.04)), (1, (0.17, 0.0, 0.0))):
    hand = C.world_point(potp, tuple(pot + Vector(local)))
    sh = C.world_point(kid, (KX + side * 0.17, KY, BASE + 0.92))
    mid = (sh + hand) / 2 + Vector((0, -0.05, -0.08))
    C.tube("karm", [tuple(sh), tuple(mid), tuple(hand)], 0.05, SKIN, smooth_path=True)
    C.ball("khand", tuple(hand), (0.06, 0.06, 0.06), SKIN)

# ---------------------------------------------------------------- light, camera
C.light("key", "AREA", (-3.0, -3.2, 3.6), 1000, (1.0, 0.8, 0.6), 2.5)
C.light("fill", "AREA", (3.5, -3.5, 1.8), 150, (0.85, 0.9, 1.0), 4.0)
C.light("sun", "SPOT", (4.0, 2.5, 2.8), 14000, (1.0, 0.6, 0.28), size=0.25, target=(0, 0, 1.0), spot_deg=45)
C.light("rimL", "AREA", (-2.5, 2.5, 3.0), 900, (1.0, 0.65, 0.35), 2.0, target=(-0.6, 0, 1.3))
C.light("wallglow", "SPOT", (0.0, 1.5, 4.5), 2500, (1.0, 0.62, 0.32), target=(-0.3, 7, 1.8), spot_deg=60)
C.world()
C.camera((0.15, -4.9, 1.4), (0.0, 0, 1.15), (0.0, -0.5, 1.1), lens=46, fstop=0.9)
C.render(OUT, RES, SAMPLES)
