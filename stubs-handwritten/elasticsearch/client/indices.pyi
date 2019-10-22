# Stubs for elasticsearch.client.indices (Python 3)
#
# NOTE: These stubs are handcrafted and tailored to the API we actually use.

from typing import Any, Dict, List, Optional

from .utils import NamespacedClient


class IndicesClient(NamespacedClient):
    def analyze(self, index: Optional[Any] = ..., body: Optional[Any] = ..., params: Optional[Any] = ...) -> Dict[
        str, Any]: ...

    def refresh(self, index: Optional[Any] = ..., params: Optional[Any] = ...): ...

    def create(self, index: Any, body: Optional[Any] = ..., params: Optional[Any] = ...,
               # this argument doesn't exist in the original method definition but is
               # added during runtime via the @query_params decorator:
               include_type_name: Optional[bool] = ...): ...

    def delete(self, index: Any, ignore: Optional[List[int]] = None, params: Optional[Any] = ...): ...

    def exists(self, index: Any, ignore: Optional[List[int]] = None, params: Optional[Any] = ...): ...

    def get_mapping(self, index: Optional[Any] = ..., doc_type: Optional[Any] = ..., params: Optional[Any] = ...,
                    # + @query_params:
                    include_type_name: Optional[bool] = ...): ...

    def get_settings(self, index: Optional[Any] = ..., name: Optional[Any] = ..., params: Optional[Any] = ...): ...
