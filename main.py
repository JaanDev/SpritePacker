import argparse
from pathlib import Path
from colorama import Fore, Style, init as colorama_init

import unpacker
import packer


def processCommand(args: argparse.Namespace) -> None:
    args.output.mkdir(exist_ok=True, parents=True)

    if args.action == "unpack":
        args.input = list(set(args.input))  # remove duplicates
        for val in args.input:
            if not val.exists() or not val.is_file():
                print(f"{Fore.RED}Input file {val} does not exist!{Style.RESET_ALL}")
            elif val.suffix != ".plist":
                print(f"{Fore.RED}Input file {val} is not a plist file!{Style.RESET_ALL}")

        unpacker.unpack(args.input, args.output)
    elif args.action == "pack":
        # packer.pack(args.input, args.original, args.output, args.padding)
        pass


if __name__ == "__main__":
    colorama_init()

    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("pack", "unpack"), help="An action to use")
    parser.add_argument("-i", "--input", nargs="+", help="Input plist files (for unpacking)/dirs (for packing)", type=Path)
    parser.add_argument("-o", "--output", help="Specify an output directory", type=Path)
    parser.add_argument("-I", "--original", nargs="*", help="Optional. Original plist files for packing", type=Path)
    parser.add_argument("-p", "--padding", help="Optional. Padding for packing (default is 2)", type=int, default=2)

    processCommand(parser.parse_args())
