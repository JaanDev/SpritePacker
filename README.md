# SpritePacker
A simple & open-source CLI tool written in Python for creating and splitting sprite sheets (only .plist format is implemented right now). The packing algorithm is binary tree bin packing (which i've coded myself :<remove-github-emojis>P).

## Installation
1. Install Python 3+
2. Clone this repository (recommended) or download it as a zip archive.
3. Run `pip install -U -r ./requirements.txt` in the repository directory to install dependencies.
4. Done.

## Usage
You can just run `python main.py` without any parameters to start in interactive mode (`exit/quit/q` to exit), then type `help` or `h` to get help. While in interactive mode, you can continuously input commands.

Or, you can just specify parameters when launching `main.py`.

Don't use `packer.py` or `unpacker.py` directly.

### Parameters:
Firstly you must specify `pack` or `unpack`.
`-i/--input`: specify input files/directories (you can specify multiple entries) splitted by spaces.
`-o/--output`: specify an output directory. It will be created if it doesnt exist.
`-I/--original`: specify original .plist files for the original `spriteOffset` field. If you don't use them, your sprites may be out-of-place (only if you are not making your own sprite sheet but editing an existing one). Only used for packing! You can just specify blank strings (`""`) to not use an original file. The number of these files must be the same as number of your inputs.
`-p/--padding`: specify padding around sprites when packing (optional). A default value is 2. You can increase it if you see some weird artifacts at the edges of your sprites.

You also may not use any of the `-i/-o/-I` params or only use some of them, then you will be able to use the file/directory picker for the remaining params.

### Example usage
`python main.py pack -o sheets -i ".\extracted\GJ_GameSheet03-uhd" -I ".\orig\GJ_GameSheet03-uhd.plist" -p 6`
`python main.py unpack -o . -i GJ_GameSheet03-uhd.plist` (the images from a plist are in `./GJ_GameSheet03-uhd` directory)
`python main.py unpack` (the input file(s) and the output dir are specified through your system's file dialog)
```
$ python main.py
Starting in interactive mode.

> pack -i ".\extracted\GJ_GameSheet03-uhd" -I ".\orig\GJ_GameSheet03-uhd.plist"
```

## Contributions
Any contributions are always welcomed =)

## My contacts
Discord: Jaan#2897 (jaan2897 in a new format)