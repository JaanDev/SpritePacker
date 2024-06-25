# SpritePacker
A simple, fast, cross-platform & open-source CLI tool written in Python for packing and unpacking sprite sheets (only .plist format is implemented right now). The packing algorithm is binary tree bin packing (which i've coded myself :<remove-github-emojis>P).

## Installation
1. Install Python 3+
2. Clone this repository (recommended) or download it as a zip archive.
3. Run `pip install -U -r ./requirements.txt` in the repository directory to install dependencies.
4. Done.

## Usage
Please run `python main.py -h` to get help for cli arguments.  
Don't use `packer.py` or `unpacker.py` directly.

Example:  
`python main.py pack -i ".\extracted\GJ_GameSheet03-uhd" -o sheets -I ".\orig\GJ_GameSheet03-uhd.plist" -p 6`  
`python main.py unpack -o . -i GJ_GameSheet03-uhd.plist` (original images are in the `./GJ_GameSheet03-uhd` directory)

Examples of the packed sheets (i hope i dont get copyright strike :skull:):
![GJ_GameSheet02-uhd](assets/GJ_GameSheet02-uhd.png)
![GJ_GameSheet03-uhd](assets/GJ_GameSheet03-uhd.png)

## Contributions
Any contributions are always welcome =)

## My contacts
Discord: jaan2897