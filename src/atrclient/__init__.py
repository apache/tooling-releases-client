from typing import Final

import atrclient.client

VERSION = atrclient.client.VERSION
main = atrclient.client.main

__all__: Final[list[str]] = ["VERSION", "main"]

del Final
del atrclient
