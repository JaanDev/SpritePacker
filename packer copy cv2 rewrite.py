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
        self.name = ""
        self.rotated = False

    def pos(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def size(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    def fits(self, other) -> bool:
        # < 0 = inf
        return self.w <= other.w and (self.h <= other.h if other.h >= 0 else True)

    def __str__(self) -> str:
        return f"({self.w}, {self.h})"

    def __repr__(self):
        return str(self)

    def copy(self):
        return Box(self.w, self.h, self.x, self.y)


# returns list of boxes and total height
def algorithm(boxes: List[Box], rect: Box, pbar: tqdm, recursive: bool = False) -> tuple[List[Box], int]:
    # current pos is at a top left corner of the available space
    pos = [rect.x, rect.y]
    line_h = boxes[0].h  # boxes[0] will be the tallest box
    total_h = line_h

    result: List[Box] = []

    while len(boxes):
        # take the first (the tallest) box in the list while also removing it from the list
        box = boxes.pop(0)

        # if a box can fit in the available space
        if box.fits(Box(rect.w - (pos[0] - rect.x), rect.h - (pos[1] - rect.y))):
            box.pos(pos[0], pos[1])  # set its pos to the current pos
        else:  # if a box doesnt fit (should go on a new line)
            # if recursive and a box doesnt fit on a new line, use `continue` to 'wait' for a box that can
            if recursive and total_h + box.h > rect.h:
                continue
            pos[1] += line_h  # go to a new line
            pos[0] = rect.x  # go to a new line
            line_h = box.h  # new line height is a current box's height as it is the tallest of the remaining boxes
            total_h += line_h
            # place current box at the start of a new line
            box.pos(pos[0], pos[1])

        #                    box.w
        #   (pos)       ^^^^^^^^^^^^^^^
        #       { ----------------------------------- }
        #       { - ... -#############-             - }
        #       { - ... -#############-             - }
        # box.h { - ... -#############-             - }
        #       { - ... -#############-             - }
        #       { - ... -#############-    free     - }
        #       { - ... ---------------    space    - } line_h
        #         - ... -             -    2        - }
        #         - ... -    free     -             - }
        #         - ... -    space    -             - }
        #         - ... -    1        -             - }
        #         - ... -             -             - }
        #         ----------------------------------- }
        #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #                         rect.w

        iteration_width = box.w  # how much to move right after this current iteration

        free_space1 = Box(box.w, line_h - box.h, box.x, box.y + box.h)
        boxes1 = [b for b in boxes if b.fits(free_space1)]
        if boxes1:
            boxes1, _ = algorithm(boxes1, free_space1, pbar, True)
            for b in boxes1:
                result.append(b)
                if b in boxes:
                    boxes.remove(b)

        free_space2 = Box(rect.w - (box.w + (box.x - rect.x)), line_h, box.x + box.w, box.y)
        boxes2 = [b for b in boxes if b.fits(free_space2)]
        if boxes2:
            boxes2, _ = algorithm(boxes2, free_space2, pbar, True)
            for b in boxes2:
                result.append(b)
                if b in boxes:
                    boxes.remove(b)

            max_x = max(boxes2, key=lambda b: b.x)  # take the rightmost box
            iteration_width = max_x.x + max_x.w

        pos[0] += iteration_width
        result.append(box)
        pbar.update()

    return (result, total_h)


def pack(inputs: List[Path], originals: List[Path], output: Path, padding: int) -> None:
    orig_plists = [plistlib.load(open(orig, "rb")) for orig in originals]

    for inp in inputs:
        boxes: List[Box] = []

        for f in inp.iterdir():
            if not f.is_file() or f.suffix != ".png":
                continue

            img = cv2.imread(str(f), cv2.IMREAD_UNCHANGED)
            h, w, *_ = img.shape
            rotated = False
            if w < h:
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

        with tqdm(total=len(boxes), ascii=" ▁▂▃▄▅▆▇█", bar_format=inp.name + ": {percentage:1.0f}% {bar} [{n_fmt}/{total_fmt}]") as pbar:
            boxes, height = algorithm(boxes.copy(), Box(width, -9999999), pbar)
        totalArea = width * height
        print(f"Free space: {(totalArea - area) / totalArea * 100:.2f}%")

        print("Creating an image")

        img = np.zeros((height, width, 4), np.uint8)

        for box in boxes:
            # img.paste(box.img, (box.x + padding, box.y + padding))
            realw, realh = box.w - padding * 2, box.h - padding * 2
            x1 = box.x + padding
            x2 = x1 + realw
            y1 = box.y + padding
            y2 = y1 + realh
            
            img[y1:y2, x1:x2] = box.img

        image_filename = f"{inp.name}.png"

        cv2.imwrite(str(output.joinpath(image_filename)), img)

        print("Creating a plist")

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
            obj = {}
            obj["aliases"] = []

            size = f"{{{(b.w if not b.rotated else b.h) - padding * 2},{(b.h if not b.rotated else b.w) - padding * 2}}}"

            orig_offset = "{0,0}"
            source_size = size
            # if orig_plist:
            for orig_plist in orig_plists:
                if b.name in orig_plist["frames"]:
                    orig_val = orig_plist["frames"][b.name]
                    if orig_val:
                        orig_offset = orig_val["spriteOffset"]
                        source_size = orig_val["spriteSourceSize"]

            obj["spriteOffset"] = orig_offset
            obj["spriteSize"] = size
            obj["spriteSourceSize"] = source_size
            obj["textureRect"] = f"{{{{{b.x + padding},{b.y + padding}}},{size}}}"
            obj["textureRotated"] = b.rotated

            plist["frames"][b.name] = obj

        with open(output.joinpath(f"{inp.name}.plist"), "wb") as f:
            plistlib.dump(plist, f)

        print("Done")
