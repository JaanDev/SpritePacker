from typing import List, Tuple
import cv2
from pathlib import Path
from tqdm import tqdm
import plistlib
from colorama import Fore, Style
from datetime import datetime

# import cProfile

# cnt = 0


# def profile(func):
#     """Decorator for run function profile"""

#     def wrapper(*args, **kwargs):
#         global cnt
#         profile_filename = f"profiles/{cnt}_{func.__name__}.prof"
#         profiler = cProfile.Profile()
#         result = profiler.runcall(func, *args, **kwargs)
#         profiler.dump_stats(profile_filename)
#         cnt += 1
#         return result

#     return wrapper


# @profile
def process_frame(name: str, value: dict, img, out_dir: Path) -> None:
    bounds_str = value["frame"] if "frame" in value else value["textureRect"]
    bounds = [int(x) for x in bounds_str.translate({ord(c): None for c in "{} "}).split(",")]

    rotated = value["rotated"] if "rotated" in value else value["textureRotated"]
    if rotated:
        bounds[2], bounds[3] = bounds[3], bounds[2]

    bounds[2] += bounds[0]
    bounds[3] += bounds[1]

    cropped = img[bounds[1] : bounds[3], bounds[0] : bounds[2]]

    if rotated:
        cropped = cv2.rotate(cropped, cv2.ROTATE_90_COUNTERCLOCKWISE)

    cv2.imwrite(str(out_dir.joinpath(name)), cropped)


def unpack(inputs: List[Path], output: Path) -> None:
    for file in inputs:
        with open(file, "rb") as f:
            plist = plistlib.load(f)

        try:
            image_path = plist["metadata"]["textureFileName"]
        except KeyError as e:
            print(f"{Fore.RED}Failed to retrieve the sheet image name from the plist: {e} does not exist{Style.RESET_ALL}")
            continue

        img = cv2.imread(str(file.parent.joinpath(image_path)), cv2.IMREAD_UNCHANGED)

        out_dir = output.joinpath(file.stem)
        out_dir.mkdir(exist_ok=True)

        # https://github.com/Changaco/unicode-progress-bars/blob/master/generator.html#L38
        # feel free to customize it =)
        for name, value in tqdm(plist["frames"].items(), ascii=" ▁▂▃▄▅▆▇█", bar_format=file.stem + ": {percentage:1.0f}% {bar} [{n_fmt}/{total_fmt}]"):
            if name == "." or name == ".." or Path(name).suffix != ".png":
                continue

            process_frame(name, value, img, out_dir)
