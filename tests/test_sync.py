# -*- coding: utf-8 -*-
"""trakt.sync functional tests"""
from datetime import datetime

import pytest

from trakt.sync import (add_to_collection, add_to_history, add_to_watchlist,
                        comment, get_collection, get_watched, get_watchlist,
                        rate, remove_from_collection, remove_from_history,
                        remove_from_watchlist)


class FakeMedia:
    """Mock media type object to use with mock sync requests"""
    media_type = 'fake'

    def __init__(self):
        self.ids = {}

    def to_json_singular(self):
        return {}

    def to_json(self):
        return {}


def test_create_comment():
    """test comment creation"""
    response = comment(FakeMedia(), 'This is a new comment', spoiler=True)
    assert response.get('comment')


def test_create_review():
    """verify that a review can be successfully created"""
    response = comment(FakeMedia(), 'This is a new comment', review=True)
    assert response.get('comment')


def test_forced_review():
    """verify that a comment is forced as a review if it's length is > 200"""
    response = comment(FakeMedia(), '*' * 201, review=False)
    assert response.get('comment')


def test_rating():
    timestamps = [datetime.now(), None]
    for timestamp in timestamps:
        response = rate(FakeMedia(), 10, timestamp)
        assert response['added'] == {
            'episodes': 2, 'movies': 1, 'seasons': 1, 'shows': 1
        }
        assert len(response['not_found']['movies']) == 1


def test_add_to_history():
    timestamps = [datetime.now(), None]
    for timestamp in timestamps:
        response = add_to_history(FakeMedia(), timestamp)


@pytest.mark.parametrize('fn,get_key', [
        (add_to_watchlist, 'added'),
        (remove_from_history, 'deleted'),
        (remove_from_watchlist, 'deleted'),
        (add_to_collection, 'added'),
        (remove_from_collection, 'deleted')
    ]
)
def test_oneliners(fn, get_key):
    media = FakeMedia()
    response = fn(media)
    assert response.get(get_key)


def test_get_watchlist_movies():
    from trakt.movies import Movie
    results = get_watchlist('movies')
    assert len(results) == 2
    assert all(isinstance(r, Movie) for r in results)
    assert results[0].title == "TRON: Legacy"
    assert results[1].title == "The Dark Knight"


def test_get_watchlist_shows():
    from trakt.tv import TVShow
    results = get_watchlist('shows')
    assert len(results) == 2
    assert all(isinstance(r, TVShow) for r in results)
    assert results[0].title == "Breaking Bad"


def test_get_watchlist_iter_pages():
    """iter_pages stops after page 1 (page 2 mock returns [])."""
    from trakt.movies import Movie
    from trakt.utils import iter_pages
    all_results = []
    for page_data in iter_pages(get_watchlist, list_type='movies'):
        all_results.extend(page_data)
    assert len(all_results) == 2
    assert all(isinstance(r, Movie) for r in all_results)


def test_get_collection_movies():
    from trakt.movies import Movie
    results = get_collection('movies')
    assert len(results) == 2
    assert all(isinstance(r, Movie) for r in results)
    assert results[0].title == "TRON: Legacy"
    assert results[1].title == "The Dark Knight"


def test_get_collection_shows():
    from trakt.tv import TVShow
    results = get_collection('shows')
    assert len(results) == 2
    assert all(isinstance(r, TVShow) for r in results)
    assert results[0].title == "Breaking Bad"


def test_get_watched_movies():
    from trakt.movies import Movie
    results = get_watched('movies')
    assert len(results) == 2
    assert all(isinstance(r, Movie) for r in results)
    assert results[0].title == "TRON: Legacy"


def test_get_watched_shows():
    from trakt.tv import TVShow
    results = get_watched('shows')
    assert len(results) == 2
    assert all(isinstance(r, TVShow) for r in results)
    assert results[0].title == "Breaking Bad"
