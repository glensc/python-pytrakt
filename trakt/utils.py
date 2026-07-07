# -*- coding: utf-8 -*-
import re
import unicodedata
from datetime import datetime, timezone
from urllib.parse import urlencode

__author__ = 'Jon Nappi, Elan Ruusamäe'
__all__ = ['slugify', 'airs_date', 'now', 'timestamp', 'extract_ids',
           'build_uri']


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


def _validate_pagination_param(name, value):
    """Validate and coerce a pagination parameter to a positive integer.

    :param name: Parameter name used in error messages.
    :param value: Value to validate.
    :return: The validated integer value.
    :raises ValueError: If value is not a valid positive integer.
    """

    try:
        # bool is a subclass of int; reject it explicitly to avoid accepting True/False.
        if isinstance(value, bool):
            raise ValueError

        # Avoid silently truncating noninteger floats (e.g., 1.9 -> 1).
        if isinstance(value, float) and not value.is_integer():
            raise ValueError

        value = int(value)
    except (TypeError, ValueError):
        raise ValueError(f'{name} must be a valid integer')

    if value < 1:
        raise ValueError(f'{name} must be a positive integer')

    return value


def build_uri(uri, page=None, limit=None, extended=None, **params):
    """Format *uri* and append pagination query parameters.

    ``page`` and ``limit`` are validated as positive integers and become query
    parameters. Remaining keyword arguments are applied via ``str.format`` on
    *uri*; ``extended`` is appended as a query parameter when provided.
    Any ``None`` values are dropped before formatting (so a missing
    placeholder will raise ``KeyError``).
    """
    params = {key: value for key, value in params.items() if value is not None}
    uri = uri.format(**params)

    query = []
    if page is not None:
        query.append(('page', _validate_pagination_param('page', page)))
    if limit is not None:
        query.append(('limit', _validate_pagination_param('limit', limit)))
    if extended:
        query.append(('extended', extended))

    if query:
        uri += ('&' if '?' in uri else '?') + urlencode(query)

    return uri
