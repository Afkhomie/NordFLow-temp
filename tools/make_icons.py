"""
make_icons.py

Utility to convert a source image (PNG or SVG) into multiple PNG sizes and a single multi-size ICO
for use in Windows installers and application icons.

Usage:
    python tools\make_icons.py --src path/to/icon.png --out installers\assets --name nodeflow

Outputs:
  installers/assets/nodeflow.ico
  installers/assets/nodeflow-16.png
  installers/assets/nodeflow-32.png
  installers/assets/nodeflow-64.png
  installers/assets/nodeflow-128.png
  installers/assets/nodeflow-256.png
  installers/assets/nodeflow-512.png

Requires Pillow and cairosvg (if converting from SVG):
    pip install pillow cairosvg

"""
import os
import argparse
from PIL import Image

try:
    import cairosvg
    HAS_CAIROSVG = True
except Exception:
    HAS_CAIROSVG = False

SIZES = [16, 32, 48, 64, 128, 256, 512]


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def svg_to_png(svg_path, png_path, size):
    # Render SVG to PNG at given size (square)
    if not HAS_CAIROSVG:
        raise RuntimeError('cairosvg is required to convert SVG files. Install with pip install cairosvg')
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size, output_height=size)


def make_icons(src, out_dir, name):
    ensure_dir(out_dir)
    base, ext = os.path.splitext(src)
    ext = ext.lower()

    # If SVG, render at largest size then downscale
    temp_png = None
    if ext == '.svg':
        if not HAS_CAIROSVG:
            raise RuntimeError('SVG source provided but cairosvg not installed.')
        temp_png = os.path.join(out_dir, f"{name}-tmp-512.png")
        svg_to_png(src, temp_png, 512)
        src_for_pil = temp_png
    else:
        src_for_pil = src

    try:
        img = Image.open(src_for_pil).convert('RGBA')
    except Exception as e:
        raise RuntimeError(f'Failed to open source image: {e}')

    png_paths = []
    for s in SIZES:
        out_png = os.path.join(out_dir, f"{name}-{s}.png")
        # Resize while keeping aspect ratio and transparent background
        resized = img.copy()
        resized.thumbnail((s, s), Image.LANCZOS)

        # Create square canvas and paste centered
        canvas = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        x = (s - resized.width) // 2
        y = (s - resized.height) // 2
        canvas.paste(resized, (x, y), resized)
        canvas.save(out_png, format='PNG')
        png_paths.append(out_png)

    # Save multi-size ICO (Pillow accepts list of sizes when saving .ico)
    ico_path = os.path.join(out_dir, f"{name}.ico")
    # Build list of images for ico (must be PIL Image objects in ascending order)
    ico_images = []
    for s in SIZES:
        p = os.path.join(out_dir, f"{name}-{s}.png")
        im = Image.open(p).convert('RGBA')
        ico_images.append(im)

    # Pillow can save multiple sizes into one .ico by providing the sizes parameter
    # Save largest as base, provide sizes tuple
    try:
        ico_images[0].save(ico_path, format='ICO', sizes=[(s, s) for s in SIZES])
    except Exception:
        # Fallback: save using first image only
        ico_images[-1].save(ico_path, format='ICO')

    # Clean temp file
    if temp_png and os.path.exists(temp_png):
        os.remove(temp_png)

    return ico_path, png_paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate ICO and PNG assets from source icon')
    parser.add_argument('--src', required=True, help='Source image path (PNG or SVG)')
    parser.add_argument('--out', default='installers/assets', help='Output directory')
    parser.add_argument('--name', default='nodeflow', help='Base name for output files')
    args = parser.parse_args()

    ico, pngs = make_icons(args.src, args.out, args.name)
    print('Created:', ico)
    for p in pngs:
        print('  ', p)
