from copy import deepcopy
import yaml
from pprint import pprint


def provide_yamlpy_functions(symbols):
    symbols["render"] = render


def render(template, *args, **kwargs):
    from yamlpy.loader import Loader
    loader = Loader(deepcopy(template))
    _arguments = template["_arguments"]
    template_args = _arguments.split()
    assert len(template_args) == len(args)
    render_args = {}
    for i, value in enumerate(template_args):
        render_args[value] = args[i]
    result = loader.resolve(render_args)[0]
    result["_internal_render"] = True
    return result
