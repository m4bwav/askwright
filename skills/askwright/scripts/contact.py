"""Put candidate images side by side in one labelled image, for one askwright question.

A gallery shows one image at a time, so a pick between candidates belongs in one image (schema.md, Media items).
This draws them in a row (up to --cols per row), each with its label above it, and scales pixel art with
nearest-neighbour so it stays crisp.

    python contact.py out.png a.png b.png c.png --labels "1 (s11)" "2 (s22)" "3 (s33)" --scale 3

Needs Pillow (`pip install pillow`); ask.py itself does not.
"""
import argparse
import sys


def contact(paths, labels, out, scale=1, cols=4, smooth=False, bg=(27, 27, 34)):
    from PIL import Image, ImageDraw, ImageFont
    ims = [Image.open(p).convert("RGBA") for p in paths]
    if scale != 1:
        method = Image.LANCZOS if smooth else Image.NEAREST
        ims = [im.resize((round(im.width * scale), round(im.height * scale)), method) for im in ims]
    cols = max(1, min(cols, len(ims)))
    rows = (len(ims) + cols - 1) // cols
    cw = max(im.width for im in ims) + 16
    # the label scales with the cell: a fixed size overlaps the next label when candidates are narrow and tall
    size = max(12, min(26, cw // 7))
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except OSError:
            font = ImageFont.load_default()
    head = size + 14
    ch = max(im.height for im in ims) + head + 8
    sheet = Image.new("RGB", (cw * cols, ch * rows), bg)
    draw = ImageDraw.Draw(sheet)
    for i, (im, lab) in enumerate(zip(ims, labels)):
        x, y = (i % cols) * cw + 8, (i // cols) * ch
        draw.text((x, y + 6), lab, fill=(230, 230, 230), font=font)
        sheet.paste(im, (x, y + head), im)
    sheet.save(out)
    return sheet.size


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("out")
    p.add_argument("images", nargs="+")
    p.add_argument("--labels", nargs="+", help="one per image (default: 1, 2, 3, ...)")
    p.add_argument("--scale", type=float, default=1)
    p.add_argument("--cols", type=int, default=4)
    p.add_argument("--smooth", action="store_true", help="smooth scaling for photos and paintings")
    a = p.parse_args()
    labels = a.labels or [str(i + 1) for i in range(len(a.images))]
    if len(labels) != len(a.images):
        sys.exit("give one label per image")
    try:
        w, h = contact(a.images, labels, a.out, a.scale, a.cols, a.smooth)
    except ImportError:
        sys.exit("contact.py needs Pillow: pip install pillow")
    print(f'{{"ok": true, "out": "{a.out}", "size": [{w}, {h}]}}')


if __name__ == "__main__":
    main()
