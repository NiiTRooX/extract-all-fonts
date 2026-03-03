# This script extracts all font attachments of a Matroska file
# Requirements: mkvtoolnix executables

import subprocess
import re
import argparse
from pathlib import Path
import sys
import json


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract all font attachments from a Matroska file."
    )
    parser.add_argument("file", type=Path, help="The MKV file to extract fonts from.")
    parser.add_argument("--out", type=Path, default=Path("."), help="Output directory for extracted fonts.")
    return parser.parse_args()


def main():
    args = parse_args()
    video = Path(args.file).resolve()
    output_dir = Path(args.out).resolve()

    if not video.is_file():
        print(f"Error: File not found: {video}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    match_extension = lambda name: re.search(r"\.(ttf|otf|ttc|otc)$", name, re.I)
    attachment_types = ('application/x-truetype-font', 'application/vnd.ms-opentype', 'font/ttf', 'font/otf', 'font/ttc', 'font/otc')

    try:
        result = subprocess.run(
            ["mkvmerge", "-J", str(video)],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print("Error running mkvmerge")
        print(e)
        sys.exit(1)

    data = json.loads(result.stdout)

    attachments = data.get("attachments", [])

    print(f"Found {len(attachments)} attachments for {video}")

    count = 0
    for attach in attachments:
        content_type = attach.get("content_type")
        file_name = attach.get("file_name")
        id = attach.get("id")
        outfile = output_dir / file_name

        extension_matches = match_extension(file_name)
        type_matches = content_type in attachment_types

        if not extension_matches and not type_matches:
            print(f"Skipping '{file_name}' ({id})...")
            continue
        elif outfile.exists():
            print(f"'{outfile}' already exists, skipping...")
            continue
        elif not extension_matches:
            print(f"Type mismatch but extension looks like font; extracting '{file_name}'...")
        elif not type_matches:
            print(f"Extension mismatch but type is font; extracting '{file_name}'...")
        else:
            print(f"Extracting '{file_name}' → {outfile}")

        try:
            subprocess.run(["mkvextract", "attachments", video, f"{id}:{outfile}"], stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"Failed to extract {file_name}: {e}")
        else:
            count += 1

    print(f"Extracted {count} fonts into '{output_dir}'.")


if __name__ == "__main__":
    main()
