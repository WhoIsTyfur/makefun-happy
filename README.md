# makefun-happy

An entry for make.fun's bounty [Make the AI judge happy](https://make.fun/bounty/ai-happy-01).

## What it does

`main.py` (Python 3.13, standard library only) writes one PNG to `/output/entry.png`
(or to `$MAKEFUN_OUTPUT_DIR/entry.png`). The picture is made ahead of time by the scripts in `art/` and
committed as `art/entry.jpg` (a JPEG: the name stays entry.png, the gate reads the first bytes). `main.py` walks every PNG chunk, checks each CRC and the size limits
(at most 1 MiB and 1024 x 1024), then writes the bytes out unchanged, so every run gives the same file.

`art/` holds the code that made the picture: no image model, only scripts written for this entry.

- `art/clay.py`: helpers for a clay-miniature look in Blender (rounded boxes, tubes, filled shapes,
  lights, depth-of-field camera, Cycles render).
- `art/card.py`: the picture in `art/entry.jpg`, a kid's crayon card for the judge (wax strokes and hatching drawn with Pillow and numpy); `art/scene2.py` to `art/scene6.py`: earlier Blender scenes, built from primitives and rendered headless.
- `art/scene.py`: an earlier scene (a robot holding out a daisy).
- `art/post.py`: the final grade (a little saturation and warmth, a soft vignette) with Pillow.
- `art/gen2d.py`: the first, flat 2D version.

## How it is scored

A gate checks that the file is a whole PNG or JPEG within the limits. Then an AI judge compares
entries two at a time, in both orders, and picks the one that makes it happier, by warmth first,
then a fresh idea, feeling, craft and how well it reads small. Entries are ranked by win rate
(Bradley-Terry) over a Swiss heat and a playoff among the top 102.

## Run it locally

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

To redraw the picture (Pillow and numpy, at dev time only):

```sh
python art/card.py out/card.png v7
python -c "from PIL import Image; Image.open('out/card.png').convert('RGB').save('art/entry.jpg', quality=93, subsampling=0, optimize=True)"
```

The Blender scenes run with `blender -b --factory-startup -P art/sceneN.py -- out/render.png 1024 200`.
