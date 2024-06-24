import argparse
from pathlib import Path
from colorama import Fore, Style, init as colorama_init

import unpacker
import packer


def processCommand(args: argparse.Namespace) -> None:
    args.output.mkdir(exist_ok=True, parents=True)
    args.input = list(set(args.input))  # remove duplicates

    if args.action == "unpack":
        for val in args.input:
            if not val.exists() or not val.is_file():
                print(f"{Fore.RED}Input file {val} does not exist!{Style.RESET_ALL}")
                return
            elif val.suffix != ".plist":
                print(f"{Fore.RED}Input file {val} is not a plist file!{Style.RESET_ALL}")
                return

        unpacker.unpack(args.input, args.output)
    elif args.action == "pack":
        args.original = list(set(args.original))  # remove duplicates

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
    parser.add_argument("-i", "--input", nargs="+", help="Input plist files (for unpacking)/dirs (for packing)", type=Path)
    parser.add_argument("-o", "--output", help="Specify an output directory", type=Path)
    parser.add_argument("-O", "--original", nargs="*",
                        help="Optional. Original plist files for packing to provide sprite offsets so changed sprites don't look offset. All of them are used for every dir", type=Path, default=[])
    parser.add_argument("-p", "--padding", help="Optional. Padding for packing (default is 2)", type=int, default=2)

    processCommand(parser.parse_args())
