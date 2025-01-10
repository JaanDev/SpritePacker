import math
from typing import List
from pathlib import Path
import cv2
import numpy as np
import plistlib
from tqdm import tqdm
import re


class Box:
    def __init__(self, w: int, h: int, x: int = 0, y: int = 0) -> None:
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.img = None
        self.rotated = False
        self.name = ""

    def pos(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def size(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    def rotatedBox(self):
        res = Box(self.h, self.w, self.x, self.y)
        res.rotated = not self.rotated
        return res

    def fits(self, other) -> bool:
        # < 0 = inf
        return self.w <= other.w and (self.h <= other.h if other.h >= 0 else True)

    def __str__(self) -> str:
        return f'({self.w}, {self.h})'

    def __repr__(self):
        return str(self)

    def copy(self):
        return Box(self.w, self.h, self.x, self.y)


def algorithm(boxes: List[Box], rect: Box) -> List[Box]:
    posx, posy = rect.x, rect.y
    lineH = boxes[0].h
    srcRect = rect.copy()

    result = []

    i = 0
    while True:
        if i >= len(boxes):
            if len(boxes) > 0:
                rect.x = srcRect.x
                rect.y += lineH
                rect.w = srcRect.w
                rect.h -= lineH

                if srcRect.h >= 0 and rect.h <= 0:
                    break

                i = 0
                posx = srcRect.x
                posy += lineH
                boxes = [b for b in boxes if b.fits(rect)]
                if len(boxes) == 0:
                    break
                lineH = boxes[i].h
            else:
                break

        b = boxes[i]

        if b.fits(rect):
            del boxes[i]
            b.pos(posx, posy)
            posx += b.w

            free_space_bottom = Box(b.w, lineH - b.h, b.x, b.y + b.h)

            fits = [x for x in boxes if x.fits(free_space_bottom)]

            if fits:
                fits2 = algorithm(fits, free_space_bottom)
                result.extend(fits2)
                for b2 in fits2:
                    boxes.remove(b2)

            result.append(b)

            rect.x += b.w
            rect.w -= b.w
        else:
            i += 1

    return result


def pack(inputs: List[Path], originals: List[Path], output: Path, padding: int) -> None:
    orig_plists = [plistlib.load(open(orig, "rb")) for orig in originals]

    for inp in inputs:
        boxes: List[Box] = []

        for f in inp.iterdir():
            if not f.is_file() or f.suffix != ".png":
                continue

            img = cv2.imread(str(f), cv2.IMREAD_UNCHANGED)
            channels = img.shape[-1] if img.ndim == 3 else 1
            if channels != 4:  # convert rgb to rgba if needed
                img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
                img[:, :, 3] = 255
            h, w, *_ = img.shape
            rotated = False
            if h > w:
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                h, w = w, h
                rotated = True
            b = Box(w + padding * 2, h + padding * 2)
            b.img = img
            b.name = f.name
            b.rotated = rotated
            boxes.append(b)

        # sort boxes by height in descending order (from tallest)
        boxes.sort(key=lambda box: box.h, reverse=True)

        area = sum([box.w * box.h for box in boxes])
        maxW = max(boxes, key=lambda box: box.w).w

        width = max(math.ceil(math.sqrt(area / 0.95)), maxW)

        boxes = algorithm(boxes.copy(), Box(width, -99999999999, 0, 0))
        mostBottom = max(boxes, key=lambda box: box.y)
        tallest = max([b for b in boxes if b.y == mostBottom.y], key=lambda b: b.h)
        height = tallest.y + tallest.h
        totalArea = width * height

        img = np.zeros((height, width, 4), np.uint8)

        for box in boxes:
            realw, realh = box.w - padding * 2, box.h - padding * 2
            x1 = box.x + padding
            x2 = x1 + realw
            y1 = box.y + padding
            y2 = y1 + realh

            img[y1:y2, x1:x2] = box.img
            # img[y1:y2, x1:x2, :] = (0, 255, 0, 255)  # for debug purposes

        image_filename = f"{inp.name}.png"

        cv2.imwrite(str(output.joinpath(image_filename)), img)

        plist = dict(
            frames={},
            metadata=dict(
                format=3,
                pixelFormat="RGBA4444",
                premultiplyAlpha=False,
                realTextureFileName=image_filename,
                size=f"{{{width},{height}}}",
                smartupdate="$none",
                textureFileName=image_filename,
            ),
        )

        for b in boxes:
            size = f"{{{(b.w if not b.rotated else b.h) - padding * 2},{(b.h if not b.rotated else b.w) - padding * 2}}}"

            orig_offset = "{0,0}"
            source_size = size
            for orig_plist in orig_plists:
                if b.name in orig_plist["frames"]:
                    orig_val = orig_plist["frames"][b.name]
                    orig_offset = orig_val["spriteOffset"]
                    source_size = orig_val["spriteSourceSize"]

            plist["frames"][b.name] = dict(
                spriteOffset=orig_offset,
                spriteSize=size,
                spriteSourceSize=source_size,
                textureRect=f"{{{{{b.x + padding},{b.y + padding}}},{size}}}",
                textureRotated=b.rotated,
                aliases=[]
            )

        with open(output.joinpath(f"{inp.name}.plist"), "wb") as f:
            plistlib.dump(plist, f)

        print(f"Done packing {inp.name}. Free space: {(totalArea - area) / totalArea * 100:.2f}%, sheet size {width}x{height}")
