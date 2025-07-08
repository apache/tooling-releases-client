import importlib.metadata
from typing import Final

import atrclient.client

main = atrclient.client.main
version = importlib.metadata.version("apache-trusted-releases")

__all__: Final[list[str]] = ["main", "version"]

del Final
del atrclient
del importlib
