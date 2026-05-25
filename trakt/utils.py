# -*- coding: utf-8 -*-
import re
import unicodedata
from datetime import datetime, timezone
from typing import Iterator, Callable, Optional, NamedTuple

import trakt._pagination as _pagination_store

__author__ = 'Jon Nappi'
__all__ = ['slugify', 'airs_date', 'now', 'timestamp', 'extract_ids',
           'validate_limit', 'Pagination', 'get_pagination', 'iter_pages']

_MAX_LIMIT = 250


class Pagination(NamedTuple):
    """Pagination metadata from a Trakt.tv API response."""
    item_count: int
    limit: int
    page: int
    page_count: int


def get_pagination() -> Optional[Pagination]:
    """Return the pagination info from the most recent paginated API response.

    Returns a :class:`Pagination` namedtuple with *item_count*, *limit*,
    *page*, and *page_count* fields, or ``None`` when the last response did
    not include ``x-pagination-*`` headers (e.g. non-paginated endpoints).
    """
    return _pagination_store.get()


def iter_pages(fn: Callable, *args, **kwargs) -> Iterator:
    """Iterate over every page returned by a paginated endpoint.

    Calls *fn* with ``page=1, 2, …`` until either the response contains an
    ``x-pagination-page-count`` header and the last page has been fetched, or
    the response is empty (fallback when no pagination headers are present).

    :param fn: A callable that accepts a *page* keyword argument and returns
        the page's data.
    :param args: Positional arguments forwarded to *fn*.
    :param kwargs: Keyword arguments forwarded to *fn* (``page`` is
        overridden on each call).
    """
    page = 1
    while True:
        kwargs['page'] = page
        data = fn(*args, **kwargs)
        if not data:
            break
        yield data
        pagination = get_pagination()
        if pagination is not None and page >= pagination.page_count:
            break
        page += 1


def validate_limit(limit):
    """Raise :class:`ValueError` if *limit* exceeds the maximum allowed value
    of 250 items per page imposed by the Trakt.tv API.
    """
    if limit is not None and limit > _MAX_LIMIT:
        raise ValueError(
            f"limit must not exceed {_MAX_LIMIT} items per page, got {limit}"
        )


def slugify(value):
    """Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.

    Adapted from django.utils.text.slugify
    """
    value = unicodedata.normalize('NFKD', value)
    # special case, "ascii" encode would just remove it
    value = value.replace("’", '-')
    value = value.encode('ascii', 'ignore').decode('utf-8')
    value = value.lower()
    value = re.sub(r'[^\w\s-]', ' ', value)
    value = re.sub(r'[-\s]+', '-', value)
    value = value.strip('-')

    return value


def airs_date(airs_at):
    """convert a timestamp of the form '2015-02-01T05:30:00.000-08:00Z' to a
    python datetime object (with time zone information removed)
    """
    if airs_at is None:
        return None
    parsed = airs_at.split('-')[:-1]
    if len(parsed) == 2:
        return datetime.strptime(airs_at[:-1], '%Y-%m-%dT%H:%M:%S.000')
    return datetime.strptime('-'.join(parsed), '%Y-%m-%dT%H:%M:%S.000')


def now():
    """Get the current day in the format expected by each :class:`Calendar`"""
    meow = datetime.now(tz=timezone.utc)
    return meow.strftime("%Y-%m-%d")


def timestamp(date_object):
    """Generate a trakt formatted timestamp from the given date object"""
    fmt = '%Y-%m-%dT%H:%M:%S.000Z'
    return date_object.strftime(fmt)


def extract_ids(id_dict):
    """Extract the inner `ids` dict out of trakt JSON responses and insert them
    into the containing `dict`. Then return the input `dict`
    """
    id_dict.update(id_dict.pop('ids', {}))
    return id_dict
