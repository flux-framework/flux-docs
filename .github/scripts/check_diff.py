#!/usr/bin/env python3

# This script checks that two directories are recursively equal
# however we only care about name (existence) and timestamp.
# Usage:
#  python .github/scripts/check_diff.py /tmp/auto_examples ./auto_examples

import argparse
import os
import fnmatch


def recursive_find(base, pattern="*.*"):
    """
    Get a list of all files in a root.

    We need full and relative paths, so just assemble that.
    """
    files = {}
    for root, _, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            fullpath = os.path.join(root, filename)
            relpath = os.path.relpath(fullpath, base)
            files[relpath] = fullpath
    return files


def get_parser():
    """
    Get a parser to retrieve two directories.
    """
    parser = argparse.ArgumentParser(
        description="🤒️ Not terribly accurate directory comparison tool."
    )
    parser.add_argument("dir_a", help="the first directory")
    parser.add_argument("dir_b", help="the second directory")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    # Both directories must exist
    for dirname in args.dir_a, args.dir_b:
        if not os.path.exists(dirname):
            sys.exit(f"😢️ {dirname} does not exist.")

    print(f"🐨️ Checking for differences between {args.dir_a} and {args.dir_b}")

    # Lookup of relative -> fullpath
    files_a = recursive_find(args.dir_a)
    files_b = recursive_find(args.dir_b)

    # The relative paths should match
    A = set(files_a)
    B = set(files_b)
    if A.difference(B):
        sys.exit(
            f"😢️ Auto examples were not updated! Difference between sets:\n{A.difference(B)}"
        )

    # Now for each file check the size
    for key, file_a in files_a.items():
        file_b = files_b[key]
        stat_a = os.stat(file_a)
        stat_b = os.stat(file_b)
        if stat_a.st_size != stat_b.st_size:
            sys.exit(
                f"😢️ Auto examples were not updated! Different size of {key}:\n{stat_a.st_size} vs. {stat_b.st_size}"
            )

    print(f"😃️ Yay! No differences between {args.dir_a} and {args.dir_b}")


if __name__ == "__main__":
    main()
