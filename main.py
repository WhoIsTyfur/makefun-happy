"""make.fun ai-happy-01 entry: write the image to /output/entry.png.

The picture is made ahead of time by the scripts in art/ and committed as
art/entry.png; this program only checks it and writes it out, so both runs
give the same bytes and the run takes well under a second.
"""
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "art", "entry.png")


def check_png(data):
    """Walk every chunk and verify its CRC, the size limits and the IEND."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    assert len(data) <= 1048576, "over 1 MiB"
    pos, seen_end = 8, False
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        (crc,) = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])
        assert zlib.crc32(kind + body) & 0xFFFFFFFF == crc, "bad CRC"
        if kind == b"IHDR":
            w, h = struct.unpack(">II", body[:8])
            assert w <= 1024 and h <= 1024, "too large"
        pos += 12 + length
        if kind == b"IEND":
            seen_end = True
            break
    assert seen_end, "no IEND"


def check_jpeg(data):
    """A JPEG must start with SOI and end with EOI, within the size limit."""
    assert data[:2] == b"\xff\xd8" and data.rstrip(b"\x00")[-2:] == b"\xff\xd9", "bad JPEG"
    assert len(data) <= 1048576, "over 1 MiB"


def load():
    """Read the committed picture (PNG preferred, JPEG accepted) and check it."""
    for name, check in (("entry.png", check_png), ("entry.jpg", check_jpeg)):
        path = os.path.join(HERE, "art", name)
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = f.read()
            check(data)
            return data
    raise SystemExit("no art/entry.png or art/entry.jpg")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    data = load()
    os.makedirs(out_dir, exist_ok=True)
    # write to a temp name, then rename, so a reader never sees half a file
    tmp = os.path.join(out_dir, ".entry.tmp")
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
