# This script extracts all font attachments of a Matroska file
# Requirements: mkvtoolnix executables

import subprocess
import re
import os.path
from collections import namedtuple
import argparse
from pathlib import Path


# User settings

print_debug = False

# End of User settings

parser = argparse.ArgumentParser()
parser.add_argument("file", type=Path)
p = parser.parse_args()
video = p.file

match_extension = lambda name: re.search(r"\.(ttf|otf|ttc|otc)$", name, re.I)
attachment_types = ('application/x-truetype-font', 'application/vnd.ms-opentype', 'font/ttf', 'font/otf', 'font/ttc', 'font/otc')

# I hate regex
regexp_track = re.compile(r"^Track ID (?P<id>\d+): (?P<type>\w+) \((?P<codec>[^\)]+)\)$", re.M)
regexp_attachment = re.compile(r"^Attachment ID (?P<id>\d+): type '(?P<type>[^']+)', size (?P<size>\d+) bytes, file name '(?P<name>.*?)'$", re.M)


def debug(*args):
    if print_debug:
        print(*args)


def mkv(tool, *params):
    cmd = ['mkv' + tool] + [str(p) for p in params]
    debug("Running:", ' '.join(cmd))
    return subprocess.check_output(cmd, universal_newlines=True)


MatroskaContainer = namedtuple("MatroskaContainer", 'tracks attachments')
Track = namedtuple("Track", 'id type codec')
Attachment = namedtuple("Attachment", 'id type size name')


def mkvidentify(video):
    identify = mkv("merge", "--identify", video)
    debug(identify)

    collect = lambda r, c: [c(*x) for x in r.findall(identify)]

    return MatroskaContainer(collect(regexp_track, Track), collect(regexp_attachment, Attachment))


def main():
    container = mkvidentify(video)
    debug(container)
    attachments = container.attachments
    print(f"Found {len(attachments)} attachments for {video}")

    count = 0
    for i, attach in enumerate(attachments):
        extension_matches = match_extension(attach.name)
        type_matches = attach.type in attachment_types

        if not extension_matches and not type_matches:
            print(f"Skipping '{attach.name}' ({attach.id})...")
            continue
        elif os.path.exists(attach.name):
            print(f"'{attach.name}' ({attach.id}) already exists, skipping...")
            continue
        elif not extension_matches:
            print(f"Type mismatch but extention of a font; still extracting... ('{attach.name}', {attach.type})")
        elif not type_matches:
            print(f"Extension mismatch but type of a font; still extracting... ('{attach.name}', {attach.type})")
        else:
            print(f"Extracting '{attach.name}'...")

        try:
            mkv("extract", "attachments", video, f"{attach.id}:{attach.name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to extract {attach.name}: {e}")
        else:
            count += 1

    print(f"Extracted {count} fonts.")


if __name__ == "__main__":
    main()
