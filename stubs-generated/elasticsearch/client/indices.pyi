# Stubs for elasticsearch.client.indices (Python 3.6)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any, Dict, List, Optional

from .utils import SKIP_IN_PATH, NamespacedClient, query_params

class IndicesClient(NamespacedClient):
    def create(self, index: Any, body: Optional[Any] = ..., params: Optional[Any] = ...) -> Any: ...