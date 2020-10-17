import sys
import yaml
from pathlib import Path
from optparse import OptionParser
from . import Loader
from .pretty import pretty_print_yaml


def parse_cmd_line():
    parser = OptionParser()
    parser.add_option(
        "-e",
        "--environ-vars",
        dest="env_vars",
        help="import values from environent variables",
        default=None,
    )
    parser.add_option(
        "-x",
        "--extra-file",
        dest="extra_file",
        help="read extra file with yaml values",
        metavar="FILE",
    )
    options, args = parser.parse_args()
    if len(args) < 1:
        print("Usage: {} file.yaml".format(sys.argv[0]))
        exit(1)
    return options, args


def main():
    options, args = parse_cmd_line()
    filename = Path(args[0])
    loader = Loader(filename, extra_file=options.extra_file, env_vars=options.env_vars)
    result = loader.resolve()
    for result_item in result:
        if len(result) > 1:
            print("---")
        output_yaml = yaml.safe_dump(result_item)
        if sys.stdout.isatty():
            pretty_print_yaml(output_yaml)
        else:
            print(output_yaml)
