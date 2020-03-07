import yaml
from pathlib import Path
from yamlpy import Loader


def collect_test_files():
    test_files = Path(__file__).parent.joinpath("files").glob("*.yaml")
    return test_files


test_files_list = [x for x in collect_test_files() if "result.yaml" not in x.name]


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
        loader = Loader(open(test_filename).read())
        data = loader.resolve()
        base_path = str(Path(test_filename)).split(".")[0]
        result_path = Path(base_path + "_result.yaml")
        expected_data = yaml.load(open(result_path).read(), yaml.FullLoader)
        # Support both result and __result for raw check
        assert data == expected_data
