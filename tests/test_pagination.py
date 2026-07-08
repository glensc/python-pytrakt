from trakt.pagination import paginate


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