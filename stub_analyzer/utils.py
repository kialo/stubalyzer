from typing import List, Optional

from mypy.nodes import ARG_STAR, ARG_STAR2, Expression

from .types import STRICT_ARG_KINDS


def get_expression_fullname(expr: Expression) -> Optional[str]:
    fullname_attr = getattr(expr, "fullname", None)

    if callable(fullname_attr):
        fullname_attr = fullname_attr()

    return fullname_attr if isinstance(fullname_attr, str) else None


def strict_kind_count(kinds: List[int]) -> int:
    return len([kind for kind in kinds if kind in STRICT_ARG_KINDS])


def arg_star_count(kinds: List[int]) -> int:
    return len([kind for kind in kinds if kind is ARG_STAR])


def arg_star2_count(kinds: List[int]) -> int:
    return len([kind for kind in kinds if kind is ARG_STAR2])
