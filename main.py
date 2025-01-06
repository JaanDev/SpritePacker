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


def processCommand(args: argparse.Namespace) -> None:
    args.output.mkdir(exist_ok=True, parents=True)

    if args.action == "unpack":
        input_files = globbed_list(args.input)

        input_files_ok = []

        for val in input_files:
            if not val.exists() or not val.is_file():
                print(f"{Fore.RED}Input file {val} does not exist, skipping!{Style.RESET_ALL}")
                continue
            elif val.suffix != ".plist":
                print(f"{Fore.RED}Input file {val} is not a plist file, skipping!{Style.RESET_ALL}")
                continue

            if args.resolution is not None:
                fname = val.name

                if not ((args.resolution == 'sd' and 'hd' not in fname and 'uhd' not in fname) or
                        (args.resolution == 'hd' and 'hd' in fname and 'uhd' not in fname) or
                        (args.resolution == 'uhd' and 'uhd' in fname)):
                    continue

            input_files_ok.append(val)

        try:
            unpacker.unpack(input_files_ok, args.output)
        except Exception as e:
            print(f"{Fore.RED}Failed to unpack files: {str(e)}!{Style.RESET_ALL}")
    elif args.action == "pack":
        input_dirs = globbed_list(args.input)

        input_dirs_ok = []

        for val in input_dirs:
            if not val.exists() or not val.is_dir():
                print(f"{Fore.RED}Input dir {val} does not exist, skipping!{Style.RESET_ALL}")
                continue

            if args.resolution is not None:
                fname = val.name

                if not ((args.resolution == 'sd' and 'hd' not in fname and 'uhd' not in fname) or
                        (args.resolution == 'hd' and 'hd' in fname and 'uhd' not in fname) or
                        (args.resolution == 'uhd' and 'uhd' in fname)):
                    continue

            input_dirs_ok.append(val)

        # !!! havent tested original files at all!

        args.original = globbed_list(args.original)

        original_ok = []

        for val in args.original:
            if not val.exists() or not val.is_file():
                print(f"{Fore.RED}Original file {val} does not exist, skipping!{Style.RESET_ALL}")
                continue
            elif val.suffix != ".plist":
                print(f"{Fore.RED}Original file {val} is not a plist file, skipping!{Style.RESET_ALL}")
                continue

            if args.resolution is not None:
                fname = val.name

                if not ((args.resolution == 'sd' and 'hd' not in fname and 'uhd' not in fname) or
                        (args.resolution == 'hd' and 'hd' in fname and 'uhd' not in fname) or
                        (args.resolution == 'uhd' and 'uhd' in fname)):
                    continue

            original_ok.append(val)

        packer.pack(input_dirs_ok, original_ok, args.output, args.padding)


if __name__ == "__main__":
    colorama_init()

    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("pack", "unpack"), help="An action to use")
    parser.add_argument("-i", "--input", nargs="+", help="Input plist files (for unpacking)/dirs (for packing). Supports globbing", type=Path)
    parser.add_argument("-o", "--output", help="Optional. Specify an output directory (default is ./output)", type=Path, default=Path("./output"))
    parser.add_argument("-O", "--original", nargs="*",
                        help="Optional. !!!not sure that it works in 2.2!!! Original plist files for packing to provide sprite offsets so changed sprites don't look out of place. "
                             "All of them are used for every dir. Supports globbing", type=Path, default=[])
    parser.add_argument("-p", "--padding", help="Optional. Padding for packing (default is 2)", type=int, default=2)
    parser.add_argument("-r", "--resolution", choices=("sd", "hd", "uhd"),
                        help="Optional. If specified, only input files/dirs of this resolution are processed (sd (low), hd, uhd)")

    args = parser.parse_args()
    processCommand(args)
