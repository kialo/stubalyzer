from collections import OrderedDict
from collections.abc import Mapping as Mapping
from collections.abc import Sequence as Sequence
from typing import Any

PY2: Any
PYPY: Any
ordered_dict = dict
ordered_dict = OrderedDict

def just_warn(*args: Any, **kw: Any) -> None: ...
def isclass(klass: Any): ...

TYPE: str

def iteritems(d: Any): ...
def metadata_proxy(d: Any): ...
def make_set_closure_cell(): ...

set_closure_cell: Any
