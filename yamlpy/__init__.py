from ._version import get_versions
from .loader import Loader

__version__ = get_versions()["version"]
del get_versions

__all__ = [Loader, __version__]
