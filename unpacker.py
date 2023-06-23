from typing import List
import plistlib
from PIL import Image
from pathlib import Path
import re
from tqdm import tqdm


def unpack(inputs: List[Path], output: Path) -> None:
    for file in inputs:
        with open(file, 'rb') as f:
            plist = plistlib.load(f)

        img = Image.open(file.parent.joinpath(
            plist["metadata"]["textureFileName"]))

        out_dir = output.joinpath(file.stem)
        if not out_dir.is_dir():
            out_dir.mkdir(parents=True, exist_ok=True)

        # https://github.com/Changaco/unicode-progress-bars/blob/master/generator.html#L38
        # feel free to customize it =)
        for name, value in tqdm(plist["frames"].items(), ascii=" ▁▂▃▄▅▆▇█", bar_format=file.stem + ': {percentage:1.0f}% {bar} [{n_fmt}/{total_fmt}]'):
            if name == "." or name == ".." or Path(name).suffix != ".png":
                continue

            bounds = [int(x) for x in re.search(
                r"\{\{(\d+),(\d+)\},\{(\d+),(\d+)\}\}", value["frame"] if "frame" in value else value["textureRect"]).groups()]

            rotated = value["rotated"] if "rotated" in value else value["textureRotated"]
            if rotated:
                bounds.insert(2, bounds.pop())

            bounds[2] += bounds[0]
            bounds[3] += bounds[1]

            cropped = img.crop(bounds)

            if rotated:
                cropped = cropped.rotate(90, expand=True)

            cropped.save(out_dir.joinpath(name))
