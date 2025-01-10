from PIL import Image, ImageDraw, ImageColor
import os
import random
import sys

# this is a script to make random colored images in a folder. this was used to make pictures for readme

f1 = sys.argv[1]

for f in os.listdir(f1):
    img = Image.open(os.path.join(f1, f))

    img2 = Image.new('RGB', img.size, ImageColor.getrgb(f"hsv({random.randint(0, 359)}, 75%, 100%)"))

    img.close()

    img2.save(os.path.join(f1, f))
