"""Main cli."""

import argparse

from .conversion import convert_file


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the MMCore configuration converter."""
    parser = argparse.ArgumentParser(description="Convert MMCore configuration files.")
    parser.add_argument("input_file", type=str, help="Input configuration file path.")
    parser.add_argument("output_file", type=str, help="Output configuration file path.")
    return parser.parse_args()


def main() -> None:
    """Convert MMCore configuration file to a different format."""
    args = parse_args()
    convert_file(args.input_file, args.output_file)
