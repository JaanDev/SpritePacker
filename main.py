import argparse
import sys
import shlex
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import unpacker
import packer


def processCommand(args: argparse.Namespace) -> None:
    if not args.output:
        root = tk.Tk()
        root.withdraw()
        args.output = Path(filedialog.askdirectory(
            mustexist=True, title="Please select an output directory"))
        root.destroy()
        if not args.output:
            print("Please specify an output directory!")
            return

    if args.action == 'unpack':
        if args.input is None:
            root = tk.Tk()
            root.withdraw()
            args.input = [Path(x) for x in filedialog.askopenfilenames(
                title="Please select input files", filetypes=[("Spritesheets", "*.plist")])]
            root.destroy()
            if not args.input:
                print("Please specify input files!")
                return
        else:
            for file in args.input:
                if not file.is_file() or file.suffix != ".plist":
                    print(
                        f'The specified input file "{file}" is not valid! Please specify .plist inputs')
                    return

        unpacker.unpack(args.input, args.output)
    elif args.action == 'pack':
        if args.input is None:
            root = tk.Tk()
            root.withdraw()
            args.input = [Path(filedialog.askdirectory(
                mustexist=True, title="Please select an input directory"))]
            root.destroy()
            if not args.input:
                print("Please select an input directory")
                return
        else:
            for file in args.input:
                if not file.is_dir():
                    print(
                        f'The specified input directory {file} is not valid! Please specify directory inputs')

        if len(args.input) != len(args.original):
            root = tk.Tk()
            root.withdraw()
            args.original = []
            for inp in args.input:
                args.original.append(Path(filedialog.askopenfilename(
                    title=f"Please select an original plist for {inp.stem} (cancel to not specify it)", filetypes=[("Spritesheets", "*.plist")])))
            root.destroy()

        packer.pack(args.input, args.original, args.output, args.padding)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=(
        'pack', 'unpack'), help='An action to use')
    parser.add_argument('-i', '--input', nargs='*',
                        help='Optional. Specify input files/dirs', type=Path)
    parser.add_argument('-I', '--original', nargs='*',
                        help='Optional. Specify original plist files. Only used for packing!', type=Path)
    parser.add_argument(
        '-o', '--output', help='Optional. Specify an output directory', type=Path)
    parser.add_argument(
        '-p', '--padding', help='Optional. Specify a padding for packing (default is 2)', type=int, default=2)

    if len(sys.argv) == 1:
        print("Starting in interactive mode.")

        while True:
            print()
            prompt = input("> ")

            if prompt.lower() in ['help', 'h']:
                parser.print_help()
                continue

            if prompt.lower() in ['exit', 'quit', 'q']:
                sys.exit(0)

            try:
                processCommand(parser.parse_args(shlex.split(prompt)))
            except SystemExit:  # dont exit on argparse arguments errors, just tell the correct usage
                pass

    processCommand(parser.parse_args())
