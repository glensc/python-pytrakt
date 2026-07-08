from trakt.pagination import paginate
from trakt.api import HttpClient


class FakeClient:
    def __init__(self, pages):
        self.pages = list(pages)
        self.urls = []

    def get(self, url, include_headers=False):
        self.urls.append((url, include_headers))
        return self.pages.pop(0)


def test_paginate_fetches_all_list_pages():
    client = FakeClient([
        ([{'title': 'One'}], {'X-Pagination-Page-Count': '3'}),
        ([{'title': 'Two'}], {'X-Pagination-Page-Count': '3'}),
        ([{'title': 'Three'}], {'X-Pagination-Page-Count': '3'}),
    ])

    result = paginate(
        'users/{user}/watched/movies',
        api=client,
        user='sean',
        limit=2,
    )

    assert result == [
        {'title': 'One'},
        {'title': 'Two'},
        {'title': 'Three'},
    ]
    assert client.urls == [
        ('users/sean/watched/movies?limit=2', True),
        ('users/sean/watched/movies?page=2&limit=2', True),
        ('users/sean/watched/movies?page=3&limit=2', True),
    ]


def test_paginate_stops_after_one_page_without_valid_page_count():
    client = FakeClient([
        ([{'title': 'One'}], {'X-Pagination-Page-Count': 'invalid'}),
        ([{'title': 'Two'}], {'X-Pagination-Page-Count': '2'}),
    ])

    result = paginate('movies/popular', api=client)

    assert result == [{'title': 'One'}]
    assert client.urls == [('movies/popular', True)]


def test_paginate_stops_after_one_page_without_page_count():
    client = FakeClient([
        ([{'title': 'One'}], {}),
        ([{'title': 'Two'}], {'X-Pagination-Page-Count': '2'}),
    ])

    result = paginate('movies/popular', api=client)

    assert result == [{'title': 'One'}]
    assert client.urls == [('movies/popular', True)]


def test_paginate_skips_none_extends_lists_and_appends_objects():
    client = FakeClient([
        (None, {'X-Pagination-Page-Count': '3'}),
        ([{'title': 'Two'}], {'X-Pagination-Page-Count': '3'}),
        ({'title': 'Three'}, {'X-Pagination-Page-Count': '3'}),
    ])

    result = paginate('movies/popular', api=client)

    assert result == [{'title': 'Two'}, {'title': 'Three'}]


def test_http_client_paginate_delegates(monkeypatch):
    def fake_paginate(url, api, **params):
        assert isinstance(api, HttpClient)
        assert url == 'movies/popular'
        assert params == {'limit': 2}
        return ['ok']

    monkeypatch.setattr('trakt.api.paginate', fake_paginate)

    client = HttpClient('https://api.trakt.tv/', session=None)

    assert client.paginate('movies/popular', limit=2) == ['ok']
