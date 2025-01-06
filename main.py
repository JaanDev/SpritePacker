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


def process_all_files(resolution: str, output_dir: str, input_files: str):
    print(f"Processing {resolution} resolution files")

    # Find all plist files based on resolution
    plist_files = []
    for file in input_files:
        if file.suffix != ".plist":
            continue

        fname = file.name

        if (resolution == 'sd' and 'hd' not in fname and 'uhd' not in fname) or \
           (resolution == 'hd' and 'hd' in fname and 'uhd' not in fname) or \
           (resolution == 'uhd' and 'uhd' in fname):
            plist_files.append(file)

    if not plist_files:
        print(f"{Fore.YELLOW}No {resolution} plist files found!{Style.RESET_ALL}")
        return

    unpacker.unpack(plist_files, output_dir)


def processCommand(args: argparse.Namespace) -> None:
    if args.output is None:
        args.output = Path("./output")

    args.output.mkdir(exist_ok=True, parents=True)

    if args.action == "unpack":
        args.input = globbed_list(args.input)

        if args.resolution is not None:
            process_all_files(args.resolution, args.output, args.input)
            return

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
            print(f"{Fore.RED}Failed to unpack files: {str(e)}!{Style.RESET_ALL}")
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
    parser.add_argument("-r", "--resolution", choices=("sd", "hd", "uhd"), help="Optional. If specified, only input files of this resolution are processed (sd (low), hd, uhd)")

    args = parser.parse_args()
    processCommand(args)
