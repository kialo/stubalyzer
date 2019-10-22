import datetime
from types import GeneratorType
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar, Union

try:
    from maya import MayaDT as _MayaDT  # type: ignore
except ImportError:
    _MayaDT = None

_FreezeTimeInputType = Union[
    str, datetime.date, datetime.timedelta, Callable, GeneratorType, _MayaDT
]
_FreezeTimeInputInternalType = Union[str, datetime.date, datetime.timedelta]

class TickingDateTimeFactory:
    time_to_freeze: datetime.datetime
    start: datetime.datetime
    def __init__(
        self, time_to_freeze: datetime.datetime, start: datetime.datetime
    ) -> None: ...
    def __call__(self) -> datetime.datetime: ...

class FrozenDateTimeFactory:
    time_to_freeze: datetime.datetime
    def __init__(self, time_to_freeze: datetime.datetime) -> None: ...
    def __call__(self) -> datetime.datetime: ...
    def tick(self, delta: datetime.timedelta = ...) -> None: ...
    def move_to(self, target_datetime: _FreezeTimeInputInternalType) -> None: ...

class StepTickTimeFactory:
    time_to_freeze: datetime.datetime
    step_width: int
    def __init__(self, time_to_freeze: datetime.datetime, step_width: int) -> None: ...
    def __call__(self) -> datetime.datetime: ...
    def tick(self, delta: Optional[datetime.timedelta] = None) -> None: ...
    def update_step_width(self, step_width: int) -> None: ...
    def move_to(self, target_datetime: _FreezeTimeInputInternalType) -> None: ...

FactoryType = Union[StepTickTimeFactory, TickingDateTimeFactory, FrozenDateTimeFactory]
CallableT = TypeVar("CallableT", bound=Callable)

class _freeze_time:
    time_to_freeze: datetime.datetime
    tz_offset: datetime.timedelta
    ignore: Tuple
    tick: bool
    auto_tick_seconds: int
    undo_changes: List[Tuple]
    modules_at_start: Set[str]
    as_arg: bool
    fake_names: Optional[Tuple]
    reals: Optional[Dict]
    def __init__(
        self,
        time_to_freeze_str: Optional[_FreezeTimeInputInternalType],
        tz_offset: Union[int, datetime.timedelta],
        ignore: List[str],
        tick: bool,
        as_arg: bool,
        auto_tick_seconds: int,
    ) -> None: ...
    def __call__(self, func: CallableT) -> CallableT: ...
    def __enter__(self) -> FactoryType: ...
    def __exit__(self, *args: Any) -> None: ...
    def start(self) -> FactoryType: ...
    def stop(self) -> None: ...
    def decorate_class(self, klass: CallableT) -> CallableT: ...
    def decorate_coroutine(self, coroutine: CallableT) -> CallableT: ...
    def decorate_callable(self, func: CallableT) -> CallableT: ...

def freeze_time(
    time_to_freeze: Optional[_FreezeTimeInputType] = ...,
    tz_offset: Union[int, datetime.timedelta] = ...,
    ignore: Optional[List[str]] = ...,
    tick: bool = ...,
    as_arg: bool = ...,
    auto_tick_seconds: int = ...,
) -> _freeze_time: ...
