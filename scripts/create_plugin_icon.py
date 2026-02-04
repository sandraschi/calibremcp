"""
Create a minimal 64x64 PNG icon for the Calibre plugin.
Uses stdlib only (no PIL). Run from repo root.
"""

import struct
import zlib


def write_png(path: str, width: int, height: int, rgba_rows: list) -> None:
    """Write a minimal valid PNG file."""

    def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk = chunk_type + data
        return (
            struct.pack(">I", len(data)) + chunk + struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)
        )

    raw = b""
    for row in rgba_rows:
        raw += b"\x00" + row  # filter byte + row
    compressed = zlib.compress(raw, 9)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    chunks = png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", compressed) + png_chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(signature + chunks)


def main():
    from pathlib import Path

    out = Path(__file__).parent.parent / "calibre_plugin" / "images" / "icon.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    w, h = 64, 64
    # Simple green (#2E8B57) square with white M
    rows = []
    for y in range(h):
        row = b""
        for x in range(w):
            if 8 <= x < 56 and 8 <= y < 56:
                # Inner: light green
                r, g, b = 46, 139, 87
            else:
                r, g, b = 255, 255, 255
            row += bytes([r, g, b, 255])
        rows.append(row)
    write_png(str(out), w, h, rows)
    print(f"Created {out}")


if __name__ == "__main__":
    main()
