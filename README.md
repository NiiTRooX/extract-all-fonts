# extract-all-fonts
This script extracts all font attachments of a Matroska file

## Requirements

- mkvtoolnix executables

## Installation with uv
```
uv tool install git+https://github.com/NiiTRooX/extract-all-fonts.git
```

## Usage
```
extract-all-fonts /path/to/mkv --out ~/.local/share/fonts
```

`--out` is optional, fonts are dumped into the current dir if left out

Only the filename is checked for duplicates
