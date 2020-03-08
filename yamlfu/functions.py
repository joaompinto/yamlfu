from copy import deepcopy
from functools import partial


def provide_yamlfu_functions(symbols, doc_path):
    symbols["render"] = partial(render, doc_path)


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
