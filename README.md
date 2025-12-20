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

The `--out` option is optional. If it is not specified, fonts will be written to the current directory.

Duplicate detection is based on the filename only.
