"""Pagination helpers for Trakt API clients."""

from trakt.utils import build_uri

__author__ = 'Elan Ruusamäe'
__all__ = ['paginate']


def page_count(headers):
    try:
        return int(headers.get('X-Pagination-Page-Count', 1))
    except (TypeError, ValueError):
        return 1


def iter_pages(client, url: str, **params):
    """Yield successive pages for a paginated GET endpoint."""
    page = 1
    while True:
        page_url = build_uri(url, **params) if page == 1 else build_uri(
            url, page=page, **params
        )
        page_data, headers = client.get(page_url, include_headers=True)
        yield page_data

        if page >= page_count(headers):
            break
        page += 1


def paginate(client, url: str, **params):
    """Return a flattened list from all pages of a paginated GET endpoint."""
    results = []
    for page_data in iter_pages(client, url, **params):
        if page_data is None:
            continue
        if isinstance(page_data, list):
            results.extend(page_data)
        else:
            results.append(page_data)
    return results
