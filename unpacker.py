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
    success = cv2.imwrite(str(output_path), cropped)

    if not success:
        print(f"{Fore.RED}cv2.imwrite returned False for {output_path}!{Style.RESET_ALL}")
    if not output_path.exists():
        print(f"{Fore.RED}File does not exist after writing: {output_path}!{Style.RESET_ALL}")


def unpack(inputs: List[Path], output: Path) -> None:
    for file in inputs:
        out_dir = output.joinpath(file.stem)

        print(f"Unpacking {file.name} => {out_dir}")
        with open(file, "rb") as f:
            plist = plistlib.load(f)

        image_path = plist["metadata"]["textureFileName"]
        img_path = file.parent.joinpath(image_path)

        if not img_path.exists():
            print(f"{Fore.RED}Image file not found: {img_path}!{Style.RESET_ALL}")
            continue

        img = cv2.imread(str(img_path), cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"{Fore.RED}Failed to load image: {img_path}!{Style.RESET_ALL}")
            continue

        out_dir.mkdir(exist_ok=True, parents=True)

        skipped = []

        for name, value in tqdm(plist["frames"].items(), ascii=" ▁▂▃▄▅▆▇█", bar_format=file.stem + ": {percentage:1.0f}% {bar} [{n_fmt}/{total_fmt}]"):
            if name == "." or name == ".." or Path(name).suffix != ".png":
                skipped.append(name)
                continue

            try:
                process_frame(name, value, img, out_dir)
            except Exception as e:
                print(f"{Fore.RED}Error processing frame {name}: {str(e)}{Style.RESET_ALL}")
                continue

        if skipped:
            print(f'{Fore.YELLOW}Skipped frames: {", ".join(skipped)}{Style.RESET_ALL}')
