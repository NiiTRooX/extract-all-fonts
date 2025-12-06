# This script extracts all font attachments of a Matroska file
# Requirements: mkvtoolnix executables

import subprocess
import re
from collections import namedtuple
import argparse
from pathlib import Path


parser = argparse.ArgumentParser(
    description="Extract all font attachments from a Matroska file."
)
parser.add_argument("file", type=Path, help="The MKV file to extract fonts from.")
parser.add_argument("--debug", action="store_true", help="Enable debug output.")
parser.add_argument("--out", type=Path, default=Path("."), help="Output directory for extracted fonts.")

args = parser.parse_args()
video = args.file
output_dir = args.out

print_debug = args.debug

# Ensure output directory exists
output_dir.mkdir(parents=True, exist_ok=True)

match_extension = lambda name: re.search(r"\.(ttf|otf|ttc|otc)$", name, re.I)
attachment_types = (
    'application/x-truetype-font', 'application/vnd.ms-opentype',
    'font/ttf', 'font/otf', 'font/ttc', 'font/otc'
)

# I hate regex
regexp_track = re.compile(r"^Track ID (?P<id>\d+): (?P<type>\w+) \((?P<codec>[^\)]+)\)$", re.M)
regexp_attachment = re.compile(r"^Attachment ID (?P<id>\d+): type '(?P<type>[^']+)', size (?P<size>\d+) bytes, file name '(?P<name>.*?)'$", re.M)


def debug(*args):
    if print_debug:
        print(*args)


def mkv(tool, *params):
    cmd = ['mkv' + tool] + [str(p) for p in params]
    debug("Running:", " ".join(cmd))
    return subprocess.check_output(cmd, universal_newlines=True)

MatroskaContainer = namedtuple("MatroskaContainer", "tracks attachments")
Track = namedtuple("Track", "id type codec")
Attachment = namedtuple("Attachment", "id type size name")


def mkvidentify(video):
    identify = mkv("merge", "--ui-language", "en", "--identify", video)
    debug("Identify output:\n" + identify)

    tracks = [Track(*x) for x in regexp_track.findall(identify)]
    attachments = [Attachment(*x) for x in regexp_attachment.findall(identify)]

    return MatroskaContainer(tracks, attachments)


def main():
    container = mkvidentify(video)
    attachments = container.attachments

    print(f"Found {len(attachments)} attachments for {video}")

    count = 0
    for attach in attachments:
        outfile = output_dir / attach.name

        extension_matches = match_extension(attach.name)
        type_matches = attach.type in attachment_types

        if not extension_matches and not type_matches:
            print(f"Skipping '{attach.name}' ({attach.id})...")
            continue
        elif outfile.exists():
            print(f"'{outfile}' already exists, skipping...")
            continue
        elif not extension_matches:
            print(f"Type mismatch but extension looks like font; extracting '{attach.name}'...")
        elif not type_matches:
            print(f"Extension mismatch but type is font; extracting '{attach.name}'...")
        else:
            print(f"Extracting '{attach.name}' → {outfile}")

        try:
            mkv("extract", "attachments", video, f"{attach.id}:{outfile}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to extract {attach.name}: {e}")
        else:
            count += 1

    print(f"Extracted {count} fonts into '{output_dir}'.")


if __name__ == "__main__":
    main()
