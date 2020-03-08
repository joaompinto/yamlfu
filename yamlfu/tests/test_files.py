import yaml
from pathlib import Path
from yamlfu import Loader


def collect_test_files():
    test_files = Path(__file__).parent.joinpath("files").glob("*.yaml")
    return test_files


test_files_list = [x for x in collect_test_files() if "result.yaml" not in x.name]
test_files_list = [x for x in test_files_list if x.name[0] != "_"]


def pytest_generate_tests(metafunc):
    id_list = []
    argvalues = []
    argnames = ["test_filename"]
    for test_file in metafunc.cls.test_files:
        id_list.append(test_file.name)
        argvalues.append(([test_file]))

    metafunc.parametrize(argnames, argvalues, ids=id_list, scope="class")


class TestFile(object):
    test_files = test_files_list

    def test_file(self, test_filename):
        loader = Loader(test_filename)
        data = loader.resolve()
        base_path = str(Path(test_filename)).split(".")[0]
        result_path = Path(base_path + "_result.yaml")
        if isinstance(data, str):
            expected_data = yaml.safe_load(open(result_path).read())
            assert data == expected_data
        elif len(data) == 1:
            expected_data = yaml.safe_load(open(result_path).read())
            assert data[0] == expected_data
        else:
            expected_data = yaml.safe_load_all(open(result_path).read())
            for i, value in enumerate(expected_data):
                assert data[i] == value
