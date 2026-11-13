"""Blender scene 2 (dev-time only): a kid crowns the robot.

  blender -b --factory-startup -P art/scene2.py -- OUT.png [RES] [SAMPLES]

A little clay kid on a stool sets a paper crown on a crouching robot's head;
the robot's screen eyes have turned into hearts.
"""
import math
import os
import sys

import bpy
from mathutils import Vector, Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clay as C  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "//render2.png"
RES = int(argv[1]) if len(argv) > 1 else 1024
SAMPLES = int(argv[2]) if len(argv) > 2 else 256
FONT = "C:/Windows/Fonts/segoeprb.ttf"

scene = C.clear()
R = math.radians

# ---------------------------------------------------------------- materials
CLAY = C.mat("clay", (0.93, 0.80, 0.62), 0.6, sss=0.15)
MINT = C.mat("mint", (0.55, 0.82, 0.74), 0.55, sss=0.1)
SCREEN = C.mat("screen", (0.02, 0.03, 0.05), 0.18, coat=0.6)
HEARTGLOW = C.mat("heartglow", (1.0, 0.35, 0.5), 0.5, emit=(1.0, 0.25, 0.42), strength=7)
GLOW = C.mat("glow", (0.5, 1.0, 0.85), 0.5, emit=(0.45, 1.0, 0.8), strength=6)
BLUSH = C.mat("blush", (1.0, 0.45, 0.55), 0.5, emit=(1.0, 0.35, 0.45), strength=2.5)
SKIN = C.mat("skin", (0.95, 0.70, 0.55), 0.55, sss=0.3)
CHEEK = C.mat("cheek", (1.0, 0.5, 0.5), 0.6)
HAIR = C.mat("hair", (0.28, 0.14, 0.07), 0.5)
DRESS = C.mat("dress", (0.85, 0.12, 0.1), 0.6, sss=0.05)
SOCK = C.mat("sock", (0.98, 0.95, 0.9), 0.7)
SHOE = C.mat("shoe", (0.25, 0.35, 0.75), 0.45)
EYE = C.mat("eye", (0.08, 0.04, 0.03), 0.4)
CROWN = C.mat("crown", (1.0, 0.68, 0.04), 0.6, sss=0.05)
GEM = C.mat("gem", (0.95, 0.2, 0.3), 0.5)
WOOD = C.mat("wood", (0.55, 0.32, 0.17), 0.45)
C.wood(WOOD)
STOOL = C.mat("stool", (0.45, 0.62, 0.85), 0.5)
WALL = C.mat("wall", (0.9, 0.55, 0.36), 0.9)
BULB = C.mat("bulb", (1, 0.7, 0.4), 0.5, emit=(1.0, 0.55, 0.2), strength=14)

# ---------------------------------------------------------------- set
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 4, 0))
bpy.context.object.data.materials.append(WOOD)
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 7, 0), rotation=(math.pi / 2, 0, 0))
bpy.context.object.data.materials.append(WALL)
for i in range(26):
    x = -4.2 + i * 0.34
    z = 3.1 + 0.55 * math.cos((x + 0.3) * 0.9) - 0.15 * math.sin(i * 1.7)
    C.ball(f"bulb{i}", (x, 6.2, z), (0.07, 0.07, 0.07), BULB)

# ---------------------------------------------------------------- robot
RX = -0.58
C.rbox("leg_l", (0.24, 0.26, 0.18), (RX - 0.22, 0, 0.09), MINT, 0.08)
C.rbox("leg_r", (0.24, 0.26, 0.18), (RX + 0.22, 0, 0.09), MINT, 0.08)
body = C.rbox("body", (0.95, 0.72, 0.78), (RX, 0, 0.55), CLAY, 0.28)
body.rotation_euler = (R(8), 0, R(15))
for dx, dz, s in ((-0.06, 0.07, 0.07), (0.06, 0.07, 0.07)):
    C.ball("chest", (RX + dx, -0.37, 0.62 + dz), (s, 0.03, s), BLUSH)
C.ball("chest", (RX, -0.37, 0.62), (0.06, 0.03, 0.06), BLUSH, rot=(0, R(45), 0))

neck = C.pivot((RX, 0, 0.95))
HZ = 1.47
hp = [C.rbox("head", (1.3, 0.95, 1.0), (RX, 0, HZ), CLAY, 0.34),
      C.rbox("screen", (1.0, 0.1, 0.68), (RX, -0.45, HZ), SCREEN, 0.18)]
for ex in (-0.22, 0.22):
    hp.append(C.heart_solid("eye", (RX + ex, -0.515, HZ + 0.05), 0.0085, 0.012, HEARTGLOW))
hp.append(C.tube("smile", C.arc(RX, HZ - 0.08, 0.12, math.pi + 0.35, 2 * math.pi - 0.35, -0.515), 0.026, GLOW))
for bx in (-0.36, 0.36):
    hp.append(C.ball("blush", (RX + bx, -0.5, HZ - 0.13), (0.08, 0.012, 0.05), BLUSH))
for side in (-1, 1):
    hp.append(C.ball("ear", (RX + side * 0.68, 0, HZ), (0.07, 0.17, 0.17), MINT))

# paper crown on top of the head
CZ = HZ + 0.5
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.33, depth=0.16, location=(RX, 0, CZ + 0.06))
band = bpy.context.object
band.data.materials.append(CROWN)
C.smooth(band)
sol = band.modifiers.new("sol", "SOLIDIFY")
sol.thickness = 0.02
hp.append(band)
for k in range(7):
    a = -math.pi / 2 + (k - 3) * 0.55
    px, py = RX + 0.33 * math.cos(a), 0.33 * math.sin(a)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.085, radius2=0.0, depth=0.2,
                                    location=(px, py, CZ + 0.24))
    sp = bpy.context.object
    sp.scale = (1, 0.25, 1)
    sp.rotation_euler = (0, 0, a + math.pi / 2)
    sp.data.materials.append(CROWN)
    C.smooth(sp)
    hp.append(sp)
    hp.append(C.ball("tip", (px, py, CZ + 0.35), (0.03, 0.03, 0.03), GEM))
hp.append(C.heart_solid("crown_heart", (RX, -0.345, CZ + 0.06), 0.0035, 0.006, GEM))
C.parent_all(hp, neck)
neck.rotation_euler = (R(12), R(12), R(22))  # bows forward, tilts and turns toward the kid
crown_front_r = C.world_point(neck, (RX + 0.24, -0.26, CZ + 0.1))
crown_side_r = C.world_point(neck, (RX + 0.34, 0.02, CZ + 0.12))

# rising hearts: the joy spilling over
for (x, z, s) in ((-1.25, 2.25, 0.006), (-0.95, 2.55, 0.0045), (-1.45, 2.75, 0.0035)):
    C.heart_solid("float", (x, -0.3, z), s, 0.01, HEARTGLOW, rot=(math.pi / 2, R(-12), 0))

# ---------------------------------------------------------------- kid on a stool
KX, KY = 0.8, -0.42
C.rbox("stool", (0.62, 0.5, 0.32), (KX, KY + 0.05, 0.16), STOOL, 0.08)
BASE = 0.32
kid = C.pivot((KX, KY, BASE))
kp = []
for side in (-1, 1):
    kp.append(C.tube("leg", [(KX + side * 0.09, KY, BASE + 0.08), (KX + side * 0.09, KY, BASE + 0.45)], 0.055, SOCK))
    kp.append(C.ball("shoe", (KX + side * 0.09, KY - 0.06, BASE + 0.07), (0.075, 0.11, 0.06), SHOE))
bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.33, radius2=0.17, depth=0.62,
                                location=(KX, KY, BASE + 0.68))
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
kp.append(C.tube("kmouth", C.arc(KX, HK - 0.06, 0.07, math.pi + 0.4, 2 * math.pi - 0.4, KY - 0.285), 0.013, EYE))
C.parent_all(kp, kid)
kid.rotation_euler = (0, 0, R(-48))  # faces left, toward the robot, three quarters to us
sh_l = C.world_point(kid, (KX - 0.17, KY, BASE + 0.92))
sh_r = C.world_point(kid, (KX + 0.17, KY, BASE + 0.92))
for name, sh, hand in (("arm_l", sh_l, crown_front_r), ("arm_r", sh_r, crown_side_r)):
    mid = (sh + hand) / 2 + Vector((0.0, -0.05, 0.12))
    C.tube(name, [tuple(sh), tuple(mid), tuple(hand)], 0.05, SKIN, smooth_path=True)
    C.ball("hand", tuple(hand), (0.065, 0.065, 0.065), SKIN)

# ---------------------------------------------------------------- light
C.light("key", "AREA", (-3.0, -3.2, 3.6), 1000, (1.0, 0.8, 0.6), 2.5)
C.light("fill", "AREA", (3.5, -3.5, 1.8), 150, (0.85, 0.9, 1.0), 4.0)
C.light("sun", "SPOT", (4.0, 2.5, 2.8), 14000, (1.0, 0.6, 0.28), size=0.25, target=(0, 0, 1.2), spot_deg=45)
C.light("wallglow", "SPOT", (0.0, 1.5, 4.5), 2500, (1.0, 0.62, 0.32), target=(-0.3, 7, 1.8), spot_deg=60)
C.world()

C.camera((0.25, -4.7, 1.3), (0.0, 0, 1.25), (0.1, -0.5, 1.5), lens=50, fstop=0.7)
C.render(OUT, RES, SAMPLES)
