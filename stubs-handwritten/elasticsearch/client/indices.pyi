# Stubs for elasticsearch.client.indices (Python 3)
#
# NOTE: These stubs are handcrafted and tailored to the API we actually use.

from typing import Any, Dict, List, Optional

from .utils import NamespacedClient


class IndicesClient(NamespacedClient):
    def create(self, index: Any, body: Optional[Any] = ..., params: Optional[Any] = ...,
               # this argument doesn't exist in the original method definition but is
               # added during runtime via the @query_params decorator:
               include_type_name: Optional[bool] = ...) -> Any: ...
