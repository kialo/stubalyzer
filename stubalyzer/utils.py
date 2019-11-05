from typing import Optional

from mypy.nodes import Expression


def get_expression_fullname(expr: Expression) -> Optional[str]:
    fullname_attr = getattr(expr, "fullname", None)

    if callable(fullname_attr):
        fullname_attr = fullname_attr()

    return fullname_attr if isinstance(fullname_attr, str) else None
