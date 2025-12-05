# extract-all-fonts
This script extracts all font attachments of a Matroska file

## Requirements

- mkvtoolnix executables
- mkvmerge output has to be English

## Installation with uv
```
uv tool install git+https://github.com/NiiTRooX/extract-all-fonts.git
```

## Usage
`extract-all-fonts /path/to/mkv`
dumps all font attachments in the current dir


Only the filename is checked for duplicates

An option for output dir might be nice to have
