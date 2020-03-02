import sys
import yaml
from pathlib import Path
from optparse import OptionParser
from . import Loader
from .pretty import pretty_print_yaml


def parse_cmd_line():
    parser = OptionParser()
    options, args = parser.parse_args()
    if len(args) < 1:
        print("Usage: {} file.yaml".format(sys.argv[0]))
        exit(1)
    return options, args


def main():
    options, args = parse_cmd_line()
    filename = Path(args[0])
    loader = Loader(filename)
    result = loader.resolve()
    output_yaml = yaml.dump(result)
    if sys.stdout.isatty():
        pretty_print_yaml(output_yaml)
    else:
        print(output_yaml)
