import yaml
from dinterpol import Template
from sys import stderr
from pathlib import Path
from .functions import provide_yamlpy_functions
from pprint import pprint


class Loader:

    def __init__(self, input_data):
        self.unresolved_strings = {}
        self.multi_doc = []
        if isinstance(input_data, dict):  # Loading a template
            self.origin_yaml = input_data
            return
        if isinstance(input_data, Path):
            with open(input_data) as yaml_file:
                input_data = yaml_file.read()
        self.origin_yaml = yaml.safe_load(input_data)

    def _scan_for_strings(self, yaml_data, yaml_path, yaml_parent):
        """ scan yaml_data for unresolved dynamic string values """
        if yaml_path:
            key_name = yaml_path[-1]
            # if is a template node it will not be rendered now
            if key_name.startswith("__"):
                return
        if isinstance(yaml_data, str):
            template = Template(yaml_data)
            try:
                if key_name.isnumeric():  # Handle list indexes
                    key_name = int(key_name)
                yaml_parent[key_name] = template.render({})
            except NameError:
                string_path = "\n".join(yaml_path)
                self.unresolved_strings[string_path] = template

        # Recursively check dics
        if isinstance(yaml_data, dict):
            for key, value in yaml_data.items():
                sub_yaml_path = yaml_path + [key]
                self._scan_for_strings(value, sub_yaml_path, yaml_data)
        # Recursively check dict
        if isinstance(yaml_data, list):
            for key, value in enumerate(yaml_data):
                sub_yaml_path = yaml_path + [str(key)]
                self._scan_for_strings(value, sub_yaml_path, yaml_data)
        return

    def _resolve_str(self):
        """ resolving a single string input """
        template = Template(self.origin_yaml)
        return template.render({})

    def generate_symbols(self, base_symbols, yaml_path):

        if base_symbols:
            return base_symbols

        parent_item, yaml_key = self._element_at_path(yaml_path)

        # Generate top item symbols to be associated with "_"
        top_item = self.origin_yaml
        top_symbols_map = {}

        # Only reference resolved symbols
        top_symbols = [k for k in top_item if k not in self.unresolved_strings]
        for symbol in top_symbols:
            top_symbols_map[symbol] = top_item[symbol]
        available_symbols = {"_": top_symbols_map}

        if isinstance(parent_item, dict):
            for slibing_key in parent_item.keys():
                # Don't allow self-references
                if slibing_key == yaml_key:
                    continue
                slibing_key_path = "\n".join(yaml_path.split("\n")[:-1] + [slibing_key])
                # Don't allow to reference unresolved strings
                if slibing_key_path in self.unresolved_strings:
                    continue
                available_symbols[slibing_key] = parent_item[slibing_key]
        provide_yamlpy_functions(available_symbols)
        return available_symbols

    def resolve(self, base_symbols={}):
        """ resolve $dynamic elements$ in strings """
        if isinstance(self.origin_yaml, str):
            return self._resolve_str()

        # Scan all strings and consider them "unresolved"
        self._scan_for_strings(self.origin_yaml, [], None)

        # Loop attempting to resolve all unresolved_strings
        while True:

            # Now attempt to render all strings
            resolved_string_paths = []
            for yaml_path, yaml_value in self.unresolved_strings.items():

                parent_item, yaml_key = self._element_at_path(yaml_path)
                parent_path = ".".join(yaml_path.split("\n")[:-1])
                available_symbols = self.generate_symbols(base_symbols, yaml_path)
                try:
                    rendered_value = yaml_value.render(available_symbols)
                except NameError:
                    print("UNRESOLVED: ", parent_path + "." + yaml_key, yaml_value)
                    # print("SYMBOLS", available_symbols)
                    pass
                else:
                    # Merge rendered content when  using an internal key name
                    if yaml_key[0] == "_" and isinstance(parent_item, dict):
                        if (
                            isinstance(rendered_value, dict)
                            and "_internal_render" in rendered_value
                        ):
                            del rendered_value["_internal_render"]
                            if parent_item == self.origin_yaml:
                                self.origin_yaml = {
                                    **self.origin_yaml,
                                    **rendered_value,
                                }
                        if (
                            isinstance(rendered_value, list)
                            and isinstance(rendered_value[0], dict)
                            and "_internal_render" in rendered_value[0]
                        ):
                            for item in rendered_value:
                                del item["_internal_render"]
                                self.multi_doc.append(item)

                    # Set the value at the path
                    # print("RESOLVED: ", parent_path + "." + yaml_key, yaml_value)
                    parent_item[yaml_key] = rendered_value
                    resolved_string_paths.append(yaml_path)

            # Remove from unresolved_strings patch which were resolved
            resolved_count = len(resolved_string_paths)
            for yaml_path in resolved_string_paths:
                del self.unresolved_strings[yaml_path]

            # No new string was resolved, nothing more to resolve
            if resolved_count == 0:
                break

        # Finished resolution with unresolved values
        if self.unresolved_strings:
            print("Unable to resolve the following items:", file=stderr)
            for path, value in self.unresolved_strings.items():
                string_path = path.replace("\n", ".")
                print(f"{string_path} : {value.template}", file=stderr)
            exit(2)

        # Delete all dict fields with leading "_"
        self._delete_internal(self.origin_yaml)

        #pprint(self.multi_doc)
        if self.multi_doc:
            return self.multi_doc
        else:
            return [self.origin_yaml]
        return result

    def _delete_internal(self, yaml_data):
        """ Delete all keys with a leading '_' """
        if isinstance(yaml_data, list):
            [self._delete_internal(i) for i in yaml_data]
        if isinstance(yaml_data, dict):
            delete_keys = []
            for key, value in yaml_data.items():
                if key[0] == "_":
                    delete_keys.append(key)
                else:
                    self._delete_internal(value)
            for keyname in delete_keys:
                del yaml_data[keyname]

    def _element_at_path(self, yaml_path):
        """ return the parent data structure and key
        by walking the yaml doc using yaml_path """
        path_parts = yaml_path.split("\n")
        parent_parts, key_part = path_parts[:-1], path_parts[-1]
        parent_item = self.origin_yaml
        for path_part in parent_parts:
            if path_part.isnumeric():
                path_part = int(path_part)
            parent_item = parent_item[path_part]
        return parent_item, key_part
