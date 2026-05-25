# -*- coding: utf-8 -*-
"""Internal thread-local store for pagination state.

This module is intentionally *not* part of the public API.  External code
should use :func:`trakt.utils.get_pagination` to read pagination metadata
after an API call.
"""

import threading
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from trakt.utils import Pagination

_state = threading.local()


def get() -> Optional["Pagination"]:
    return getattr(_state, "current", None)


def set(pagination: Optional["Pagination"]) -> None:  # noqa: A001
    _state.current = pagination
