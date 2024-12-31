import argparse
from pathlib import Path
from colorama import Fore, Style, init as colorama_init
from glob import glob
from typing import List
import os
import subprocess

import unpacker
import packer


def globbed_list(p: List[Path]) -> List[Path]:
    ret = []
    for el in p:
        ret.extend(map(Path, glob(str(el))))
    return list(dict.fromkeys(ret))  # remove duplicates


def process_all_files(resolution: str, output_dir: str, input_folder: str):
    print(f"{Fore.CYAN}Processing {resolution} resolution files from {input_folder} to {output_dir}{Style.RESET_ALL}")
    
    print(resolution, input_folder, output_dir)

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True, parents=True)
    
    # Find all plist files based on resolution
    plist_files = []
    for file in os.listdir(input_folder):
        if not file.endswith(".plist"):
            continue
            
        if resolution == "sd" and "hd" not in file and "uhd" not in file:
            file_path = os.path.join(input_folder, file)
            plist_files.append(file_path)
        elif resolution == "hd" and "hd" in file and "uhd" not in file:
            file_path = os.path.join(input_folder, file)
            plist_files.append(file_path)
        elif resolution == "uhd" and "uhd" in file:
            file_path = os.path.join(input_folder, file)
            plist_files.append(file_path)

    if not plist_files:
        print(f"{Fore.YELLOW}No {resolution} plist files found{Style.RESET_ALL}")
        return
        
    # Process each plist file
    successful = 0
    failed = 0
    from tqdm import tqdm
    progress = tqdm(total=len(plist_files), desc="Processing files")
    for plist_file in plist_files:
        cmd = ["python", "main.py", "unpack", "-o", output_dir, "-i", plist_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            successful += 1
        else:
            print(f"{Fore.RED}Failed to unpack {plist_file}: {result.stderr}{Style.RESET_ALL}")
            failed += 1
        progress.update(1)
    progress.close()

    print(f"\n{Fore.GREEN}Successfully processed: {successful} files{Style.RESET_ALL}")
    if failed > 0:
        print(f"{Fore.RED}Failed to process: {failed} files{Style.RESET_ALL}")


def processCommand(args: argparse.Namespace) -> None:
    if args.output is None:
        args.output = Path("./output")
        
    args.output.mkdir(exist_ok=True, parents=True)

    if args.action == "unpack":
        if args.all:
            process_all_files(args.resolution, args.output, args.input_folder)
            return

        args.input = globbed_list(args.input)
        
        for val in args.input:
            if not val.exists() or not val.is_file():
                print(f"{Fore.RED}Input file {val} does not exist!{Style.RESET_ALL}")
                return
            elif val.suffix != ".plist":
                print(f"{Fore.RED}Input file {val} is not a plist file!{Style.RESET_ALL}")
                return

        try:
            unpacker.unpack(args.input, args.output)
        except Exception as e:
            print(f"{Fore.RED}Failed to unpack files: {str(e)}{Style.RESET_ALL}")
    elif args.action == "pack":
        args.input = globbed_list(args.input)
        args.original = globbed_list(args.original)

        for val in args.input:
            if not val.exists() or not val.is_dir():
                print(f"{Fore.RED}Input dir {val} does not exist!{Style.RESET_ALL}")
                return

        for val in args.original:
            if not val.exists() or not val.is_file():
                print(f"{Fore.RED}Original file {val} does not exist!{Style.RESET_ALL}")
                return
            elif val.suffix != ".plist":
                print(f"{Fore.RED}Original file {val} is not a plist file!{Style.RESET_ALL}")
                return

        packer.pack(args.input, args.original, args.output, args.padding)


if __name__ == "__main__":
    colorama_init()

    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("pack", "unpack"), help="An action to use")
    parser.add_argument("-i", "--input", nargs="+", help="Input plist files (for unpacking)/dirs (for packing). Supports globbing", type=Path)
    parser.add_argument("-o", "--output", help="Specify an output directory", type=Path, default=None)
    parser.add_argument("-O", "--original", nargs="*",
                        help="Optional. Original plist files for packing to provide sprite offsets so changed sprites don't look offset. All of them are used for every dir. Supports globbing", type=Path, default=[])
    parser.add_argument("-p", "--padding", help="Optional. Padding for packing (default is 2)", type=int, default=2)
    parser.add_argument("-resolution", choices=("sd", "hd", "uhd"), default="sd", help="Resolution to process when using --all (sd: no hd/uhd, hd: hd only, uhd: uhd only)")
    parser.add_argument("-input-folder", help="Input folder containing plist files when using --all", type=str, default="./assets")
    parser.add_argument("--all", action="store_true", help="Process all plist files of specified resolution")

    args = parser.parse_args()
    processCommand(args)
