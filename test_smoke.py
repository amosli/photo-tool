from PIL import Image, ImageDraw
from photo_tool import create_photo_layout
import os

# create a test input image in the workspace
infile = os.path.join(os.getcwd(), 'smoke_test_input.jpg')
if not os.path.exists(infile):
    img = Image.new('RGB', (2048, 2048), '#88c0d0')
    d = ImageDraw.Draw(img)
    d.ellipse([524, 524, 1524, 1524], fill='#e06c75')
    img.save(infile)
    print('Created test image:', infile)
else:
    print('Using existing test image:', infile)

# Run layout: uses automatic output naming
create_photo_layout(infile, output_path=None, photo_type='1寸 (25x35 mm)', spacing_mm=2, dpi=300, paper_size_mm=(102,152))

print('Smoke check complete')
