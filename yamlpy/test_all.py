# Check that the package version can be obtained and evalutes to 'True'
from . import __version__
from . import Loader


def test_version():
    assert __version__


def test_load_slibings():
    test_loader = Loader(
        """
    red: ok
    blue: not-$red$
    yellow:
        fruit: banana
    fruit: $yellow.fruit$
    """
    )
    result = test_loader.resolve()
    assert result["blue"] == "not-ok"
    assert result["fruit"] == "banana"


def test_load_base():
    test_loader = Loader(
        """
    other:
        color: blue
    my:
        config:
            color: $_.other.color.upper()$
    """
    )
    result = test_loader.resolve()
    assert result["my"]["config"]["color"] == "BLUE"
