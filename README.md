# makefun-happy

An entry for make.fun's bounty [Make the AI judge happy](https://make.fun/bounty/ai-happy-01).

## What it does

`main.py` (Python 3.13, standard library only) writes one PNG to `/output/entry.png`
(or to `$MAKEFUN_OUTPUT_DIR/entry.png`). The picture is made ahead of time by the scripts in `art/` and
committed as `art/entry.png`. `main.py` walks every PNG chunk, checks each CRC and the size limits
(at most 1 MiB and 1024 x 1024), then writes the bytes out unchanged, so every run gives the same file.

`art/` holds the code that made the picture: no image model, only scripts written for this entry.

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

To redraw the picture, run the generator in `art/` (it needs Pillow at dev time only) and copy the
result to `art/entry.png`.
