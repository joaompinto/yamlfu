from pathlib import Path
from yamlpy import Loader


def collect_test_files():
    test_files = Path(__file__).parent.joinpath("files").glob("*.yaml")
    return test_files


test_files_list = collect_test_files()


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
        # Support both result and __result for raw check
        result = data.get("__result", None) or data["result"]
        assert(data["input"] == result)
