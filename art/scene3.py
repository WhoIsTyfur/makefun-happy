"""Blender scene 3 (dev-time only): a surprise party for the judge.

  blender -b --factory-startup -P art/scene3.py -- OUT.png [RES] [SAMPLES] [BANNER]

The robot has just walked in: a kid in a party hat throws confetti under a
hand-painted banner, and the robot's hands fly to its cheeks.
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
OUT = argv[0] if argv else "//render3.png"
RES = int(argv[1]) if len(argv) > 1 else 1024
SAMPLES = int(argv[2]) if len(argv) > 2 else 256
BANNER = argv[3] if len(argv) > 3 else "THANK YOU, JUDGE!"
FONT = "C:/Windows/Fonts/segoeprb.ttf"
R = math.radians
rng = random.Random(7)

scene = C.clear()

# ---------------------------------------------------------------- materials
CLAY = C.mat("clay", (0.93, 0.80, 0.62), 0.6, sss=0.15)
MINT = C.mat("mint", (0.55, 0.82, 0.74), 0.55, sss=0.1)
SCREEN = C.mat("screen", (0.02, 0.03, 0.05), 0.18, coat=0.6)
STAR = C.mat("star", (1.0, 0.85, 0.3), 0.5, emit=(1.0, 0.8, 0.25), strength=8)
GLOW = C.mat("glow", (0.5, 1.0, 0.85), 0.5, emit=(0.45, 1.0, 0.8), strength=6)
BLUSH = C.mat("blush", (1.0, 0.45, 0.55), 0.5, emit=(1.0, 0.35, 0.45), strength=2.5)
SKIN = C.mat("skin", (0.95, 0.70, 0.55), 0.55, sss=0.3)
CHEEK = C.mat("cheek", (1.0, 0.5, 0.5), 0.6)
HAIR = C.mat("hair", (0.28, 0.14, 0.07), 0.5)
SHIRT = C.mat("shirt", (0.2, 0.45, 0.9), 0.6)
PANTS = C.mat("pants", (0.95, 0.75, 0.2), 0.6)
SHOE = C.mat("shoe", (0.85, 0.15, 0.15), 0.45)
EYE = C.mat("eye", (0.08, 0.04, 0.03), 0.4)
MOUTH = C.mat("mouth", (0.35, 0.06, 0.06), 0.5)
TONGUE = C.mat("tongue", (1.0, 0.45, 0.45), 0.5)
HAT1 = C.mat("hat1", (0.95, 0.25, 0.45), 0.6)
HAT2 = C.mat("hat2", (1.0, 0.85, 0.2), 0.6)
PAPER = C.mat("paper", (0.98, 0.95, 0.88), 0.75)
PAINT = C.mat("paint", (0.22, 0.0, 0.025), 0.5)
STRING = C.mat("string", (0.5, 0.35, 0.25), 0.8)
WOOD = C.mat("wood", (0.55, 0.32, 0.17), 0.45)
C.wood(WOOD)
WALL = C.mat("wall", (0.9, 0.55, 0.36), 0.9)
BULB = C.mat("bulb", (1, 0.7, 0.4), 0.5, emit=(1.0, 0.55, 0.2), strength=14)
CONF = [C.mat(f"conf{i}", c, 0.5) for i, c in enumerate(
    [(0.95, 0.2, 0.35), (1.0, 0.8, 0.1), (0.2, 0.6, 1.0), (0.3, 0.85, 0.45), (0.75, 0.35, 0.95)])]
BALLOON = [C.mat("bal0", (0.95, 0.15, 0.25), 0.25, coat=0.8), C.mat("bal1", (1.0, 0.75, 0.1), 0.25, coat=0.8)]

# ---------------------------------------------------------------- set
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 4, 0))
bpy.context.object.data.materials.append(WOOD)
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 7, 0), rotation=(math.pi / 2, 0, 0))
bpy.context.object.data.materials.append(WALL)
for i in range(26):
    x = -4.2 + i * 0.34
    z = 2.2 + 0.4 * math.cos((x + 0.3) * 0.9) - 0.12 * math.sin(i * 1.7)
    C.ball(f"bulb{i}", (x, 6.2, z), (0.07, 0.07, 0.07), BULB)

# ---------------------------------------------------------------- banner
# a long paper strip hung from two pins, sagging a little, letters painted on
BW, BZ, BY = 3.2, 2.72, 0.5
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, BY, BZ), rotation=(math.pi / 2, 0, 0))
ban = bpy.context.object
ban.scale = (BW, 0.5, 1)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.subdivide(number_cuts=40)
bpy.ops.object.mode_set(mode="OBJECT")
for v in ban.data.vertices:  # sag and a gentle wave
    x = v.co.x
    v.co.y += -0.06 * (1 - (2 * x / BW) ** 2) + 0.03 * math.sin(x * 5)
ban.data.materials.append(PAPER)
sol = ban.modifiers.new("sol", "SOLIDIFY")
sol.thickness = 0.01
C.smooth(ban)
for side in (-1, 1):
    C.tube("str", [(side * BW / 2, BY, BZ + 0.2), (side * (BW / 2 + 0.6), BY + 0.4, BZ + 0.9)], 0.008, STRING)
    C.ball("pin", (side * (BW / 2 - 0.08), BY - 0.03, BZ + 0.18), (0.035, 0.035, 0.035), CONF[1])
letters = C.text("banner_text", BANNER, (0, BY - 0.12, BZ - 0.02), 0.36, PAINT, FONT)
letters.data.extrude = 0.004
letters.data.bevel_depth = 0.007
# bend the letters with the paper: a curve-free approximation, small lean per glyph is enough
letters.data.offset_y = 0.0

# ---------------------------------------------------------------- robot
RX = -0.62
C.rbox("leg_l", (0.24, 0.26, 0.3), (RX - 0.22, 0, 0.15), MINT, 0.08)
C.rbox("leg_r", (0.24, 0.26, 0.3), (RX + 0.22, 0, 0.15), MINT, 0.08)
body = C.rbox("body", (0.95, 0.72, 0.78), (RX, 0, 0.68), CLAY, 0.28)
neck = C.pivot((RX, 0, 1.08))
HZ = 1.6
hp = [C.rbox("head", (1.3, 0.95, 1.0), (RX, 0, HZ), CLAY, 0.34),
      C.rbox("screen", (1.0, 0.1, 0.68), (RX, -0.45, HZ), SCREEN, 0.18)]


def star_pts(r, n=5, inner=0.45):
    pts = []
    for i in range(2 * n):
        a = math.pi / 2 + i * math.pi / n
        rr = r if i % 2 == 0 else r * inner
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    return pts


for ex in (-0.22, 0.22):
    hp.append(C.flat_solid("eye", star_pts(0.13), (RX + ex, -0.512, HZ + 0.06), 0.012, STAR))
hp.append(C.flat_solid("grin", C.grin_pts(0.15, 0.13), (RX, -0.512, HZ - 0.08), 0.01, GLOW))
for bx in (-0.38, 0.38):
    hp.append(C.ball("blush", (RX + bx, -0.5, HZ - 0.15), (0.07, 0.012, 0.045), BLUSH))
for side in (-1, 1):
    hp.append(C.ball("ear", (RX + side * 0.68, 0, HZ), (0.07, 0.17, 0.17), MINT))
C.parent_all(hp, neck)
neck.rotation_euler = (R(-6), R(-6), R(14))  # leans back a touch in surprise, turns to the kid
# hands fly up to its cheeks
for side in (-1, 1):
    cheek = C.world_point(neck, (RX + side * 0.6, -0.42, HZ - 0.36))
    sh = Vector((RX + side * 0.5, -0.02, 0.92))
    mid = Vector((RX + side * 0.8, -0.45, 0.95))
    C.tube("rarm", [tuple(sh), tuple(mid), tuple(cheek)], 0.08, MINT, smooth_path=True)
    C.ball("rhand", tuple(cheek), (0.12, 0.12, 0.12), CLAY)

# ---------------------------------------------------------------- kid with a party hat
KX, KY, BASE = 0.95, -0.45, 0.0
kid = C.pivot((KX, KY, BASE))
kp = []
for side in (-1, 1):
    kp.append(C.tube("leg", [(KX + side * 0.1, KY, BASE + 0.08), (KX + side * 0.1, KY, BASE + 0.5)], 0.07, PANTS))
    kp.append(C.ball("shoe", (KX + side * 0.1, KY - 0.06, BASE + 0.07), (0.085, 0.12, 0.065), SHOE))
kp.append(C.rbox("shirt", (0.5, 0.36, 0.5), (KX, KY, BASE + 0.75), SHIRT, 0.15))
HK = BASE + 1.28
kp.append(C.ball("head", (KX, KY, HK), (0.3, 0.29, 0.29), SKIN))
kp.append(C.ball("hair", (KX, KY + 0.05, HK + 0.07), (0.31, 0.28, 0.26), HAIR))
kp.append(C.ball("bangs", (KX - 0.05, KY - 0.13, HK + 0.19), (0.22, 0.12, 0.09), HAIR, rot=(R(-20), 0, R(10))))
for ex in (-0.1, 0.1):
    kp.append(C.tube("keye", C.arc(KX + ex, HK + 0.02, 0.045, 0.2, math.pi - 0.2, KY - 0.283), 0.012, EYE))
    kp.append(C.ball("kcheek", (KX + ex * 1.6, KY - 0.255, HK - 0.07), (0.055, 0.02, 0.035), CHEEK))
kp.append(C.flat_solid("kmouth", C.grin_pts(0.075, 0.075), (KX, KY - 0.278, HK - 0.055), 0.012, MOUTH))
kp.append(C.ball("tongue", (KX, KY - 0.283, HK - 0.105), (0.04, 0.008, 0.02), TONGUE))
# striped party hat, a little tilted, with a pompom
for k in range(4):
    z0 = HK + 0.2 + k * 0.1
    r0, r1 = 0.18 * (1 - k / 4), 0.18 * (1 - (k + 1) / 4)
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r0, radius2=r1, depth=0.1,
                                    location=(KX + 0.04, KY, z0 + 0.05), rotation=(0, R(12), 0))
    hat = bpy.context.object
    hat.data.materials.append(HAT1 if k % 2 == 0 else HAT2)
    C.smooth(hat)
    kp.append(hat)
kp.append(C.ball("pompom", (KX + 0.13, KY, HK + 0.62), (0.05, 0.05, 0.05), HAT2))
C.parent_all(kp, kid)
kid.rotation_euler = (0, 0, R(-35))
# both arms flung up, throwing confetti
for side in (-1, 1):
    sh = C.world_point(kid, (KX + side * 0.24, KY, BASE + 0.92))
    hand = C.world_point(kid, (KX + side * 0.48, KY - 0.1, BASE + 1.72))
    mid = (sh + hand) / 2 + Vector((side * 0.1, 0, -0.05))
    C.tube("karm", [tuple(sh), tuple(mid), tuple(hand)], 0.055, SHIRT, smooth_path=True)
    C.ball("khand", tuple(hand), (0.07, 0.07, 0.07), SKIN)

# confetti in the air: small flat squares and curls, mostly above and between them
for i in range(70):
    x = rng.uniform(-1.6, 1.8)
    z = rng.uniform(1.5, 2.45)
    y = rng.uniform(-1.0, 0.2)
    bpy.ops.mesh.primitive_plane_add(size=0.06, location=(x, y, z),
                                     rotation=(rng.uniform(0, 3), rng.uniform(0, 3), rng.uniform(0, 3)))
    cf = bpy.context.object
    cf.scale = (1, 0.6, 1)
    cf.data.materials.append(CONF[i % len(CONF)])
    cf.modifiers.new("s", "SOLIDIFY").thickness = 0.004

# two balloons at the side
for (x, y, z, m) in ((-1.75, 0.6, 2.05, BALLOON[0]), (-1.42, 0.9, 2.3, BALLOON[1])):
    C.ball("balloon", (x, y, z), (0.24, 0.24, 0.3), m)
    C.tube("bstring", [(x, y, z - 0.3), (x + 0.1, y - 0.1, z - 1.0), (x + 0.02, y - 0.2, 0.0)], 0.006, STRING,
           smooth_path=True)

# ---------------------------------------------------------------- light, camera
C.light("key", "AREA", (-3.0, -3.2, 3.6), 1100, (1.0, 0.8, 0.6), 2.5)
C.light("fill", "AREA", (3.5, -3.5, 1.8), 160, (0.85, 0.9, 1.0), 4.0)
C.light("sun", "SPOT", (4.0, 2.5, 2.8), 12000, (1.0, 0.6, 0.28), size=0.25, target=(0, 0, 1.2), spot_deg=45)
C.light("rimL", "AREA", (-2.5, 2.5, 3.0), 900, (1.0, 0.65, 0.35), 2.0, target=(-0.5, 0, 1.3))
C.light("bannerlight", "AREA", (0, -2.0, 4.2), 120, (1.0, 0.9, 0.75), 2.0, target=(0, 0.5, 2.7))
C.world()
C.camera((0.1, -5.6, 1.45), (0.05, 0, 1.5), (0.0, 0.0, 1.9), lens=50, fstop=2.2)
C.render(OUT, RES, SAMPLES)
