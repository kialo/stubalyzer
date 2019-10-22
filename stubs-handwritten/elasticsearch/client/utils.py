# Stubs for elasticsearch.client.utils (Python 3)
#
# NOTE: These stubs are handcrafted and tailored to the API we actually use.

from typing import Any


class NamespacedClient:
    client: Any = ...

    def __init__(self, client) -> None:
        ...

    @property
    def transport(self):
        ...
