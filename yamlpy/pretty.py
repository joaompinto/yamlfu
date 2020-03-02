""" pretty print for complex data """
from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import YamlLexer


def pretty_print_yaml(yaml_content):
    print(
        highlight(
            yaml_content, YamlLexer(), TerminalTrueColorFormatter(style="monokai")
        )
    )
