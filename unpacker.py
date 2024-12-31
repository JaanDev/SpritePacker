from typing import List, Tuple
import cv2
from pathlib import Path
from tqdm import tqdm
import plistlib
from colorama import Fore, Style
from datetime import datetime

def process_frame(name: str, value: dict, img, out_dir: Path) -> None:
    bounds_str = value["frame"] if "frame" in value else value["textureRect"]
    bounds = [int(x) for x in bounds_str.translate({ord(c): None for c in "{} "}).split(",")]

    rotated = value["rotated"] if "rotated" in value else value["textureRotated"]
    if rotated:
        bounds[2], bounds[3] = bounds[3], bounds[2]

    bounds[2] += bounds[0]
    bounds[3] += bounds[1]

    cropped = img[bounds[1]:bounds[3], bounds[0]:bounds[2]]

    if rotated:
        cropped = cv2.rotate(cropped, cv2.ROTATE_90_COUNTERCLOCKWISE)

    output_path = out_dir.joinpath(name)
    print(f"Writing to {output_path}")  # Debug print
    success = cv2.imwrite(str(output_path), cropped)
    
    if not success:
        print(f"cv2.imwrite returned False for {output_path}")
    if not output_path.exists():
        print(f"File does not exist after writing: {output_path}")


def unpack(inputs: List[Path], output: Path) -> None:
    print(f"Output directory: {output}")  # Debug print
    output.mkdir(exist_ok=True, parents=True)

    for file in inputs:
        print(f"Processing file: {file}")  # Debug print
        with open(file, "rb") as f:
            plist = plistlib.load(f)

        image_path = plist["metadata"]["textureFileName"]
        img_path = file.parent.joinpath(image_path)
        print(f"Looking for image at: {img_path}")  # Debug print

        if not img_path.exists():
            print(f"Image file not found: {img_path}")
            continue

        img = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Failed to load image: {img_path}")
            continue

        out_dir = output.joinpath(file.stem)
        out_dir.mkdir(exist_ok=True, parents=True)
        print(f"Created output directory: {out_dir}")  # Debug print

        for name, value in tqdm(plist["frames"].items(), ascii=" ▁▂▃▄▅▆▇█", bar_format=file.stem + ": {percentage:1.0f}% {bar} [{n_fmt}/{total_fmt}]"):
            if name == "." or name == ".." or Path(name).suffix != ".png":
                continue

            try:
                process_frame(name, value, img, out_dir)
            except Exception as e:
                print(f"Error processing frame {name}: {str(e)}")
                continue
