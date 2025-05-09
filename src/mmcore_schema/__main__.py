"""Main cli."""

import argparse

from mmcore_schema.mmconfig import MMConfig

from .conversion import convert_file

try:
    from rich import print
except ImportError:
    pass


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the MMCore configuration converter."""
    parser = argparse.ArgumentParser(description="Convert MMCore configuration files.")
    parser.add_argument("input_file", type=str, help="Input configuration file path.")
    parser.add_argument(
        "output_file",
        type=str,
        help=(
            "Output configuration file path. "
            "If not provided, the output will be printed to the console in JSON."
        ),
        default=None,
        nargs="?",
    )
    parser.add_argument(
        "--include-unset",
        action="store_true",
        help="Include unset fields in the output configuration file.",
    )
    parser.add_argument(
        "--exclude-defaults",
        action="store_true",
        help="Exclude default values from the output configuration file.",
    )
    return parser.parse_args()


def main() -> None:
    """Convert MMCore configuration file to a different format."""
    args = parse_args()
    if args.output_file is None:
        cfg = MMConfig.from_file(args.input_file)
        print(cfg.model_dump_json(indent=2))
    else:
        convert_file(
            args.input_file,
            args.output_file,
            exclude_unset=not args.include_unset,
            exclude_defaults=args.exclude_defaults,
        )
