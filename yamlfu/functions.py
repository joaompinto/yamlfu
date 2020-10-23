from copy import deepcopy
from functools import partial
import yaml


def provide_yamlfu_functions(symbols, doc_path):
    symbols["render"] = partial(render, doc_path)
    symbols["raw_render"] = partial(raw_render, doc_path)


def raw_render(doc_path, template, *args, **kwargs):
    load_filename = doc_path.joinpath(template)
    with open(load_filename) as yaml_file:
        input_data = yaml_file.read()
    result = yaml.safe_load(input_data)
    if isinstance(result, dict):
        print("SET RAW")
        result["__raw__"] = True
    return result


def render(doc_path, template, *args, **kwargs):
    from yamlfu.loader import Loader

    loader = Loader(deepcopy(template))

    if isinstance(template, str):
        from .loader import Loader

        load_filename = doc_path.joinpath(template)
        loader = Loader(load_filename)
        return loader.resolve()[0]

    _arguments = template["_arguments"]
    template_args = _arguments.split()
    assert len(template_args) == len(args)
    render_args = {}
    for i, value in enumerate(template_args):
        render_args[value] = args[i]
    result = loader.resolve(render_args)[0]
    result["_internal_render"] = True
    return result
