# -*- coding: utf-8 -*-
from copy import deepcopy

import pytest
import trakt
from trakt.movies import Movie
from trakt.people import Person
from trakt.tv import TVEpisode, TVSeason, TVShow
from trakt.users import (PublicList, Request, User, UserList, get_all_requests,
                         get_user_settings)


def test_user_settings():
    settings = get_user_settings()
    assert isinstance(settings, dict)


def test_requests():
    getters = [get_all_requests, User('sean').get_follower_requests]
    for getter in getters:
        requests = getter()
        assert isinstance(requests, list)
        assert all([isinstance(r, Request) for r in requests])
        for request in requests:
            r = request.approve()
            assert r is None
            r = request.deny()
            assert r is None


def test_user():
    sean = User('sean')
    assert sean.username == 'sean'
    assert str(sean) == '<User>: sean'


def test_user_collections():
    sean = User('sean')
    for _ in range(2):
        assert all([isinstance(m, Movie) for m in sean.movie_collection])
        assert all([isinstance(s, TVShow) for s in sean.show_collection])


def test_user_list():
    sean = User('sean')
    assert all([isinstance(l, UserList) for l in sean.lists])

    data = dict(name='Star Wars in machete order',
                description='Some descriptive text',
                privacy='public',
                display_numbers=True)
    # create list
    l = UserList.create(creator=sean.username, **data)
    for k, v in data.items():
        assert getattr(l, k) == v

    # get list
    l = UserList.get(data['name'], sean.username)
    l = sean.get_list(data['name'])
    for k, v in data.items():
        assert getattr(l, k) == v

    # enumerate list items
    instancetypes = (Movie, TVShow, TVSeason, TVEpisode, Person)
    assert all([isinstance(k, instancetypes) for k in l])

    # PUT to add and remove items from list
    l.add_items()
    for k, v in data.items():
        assert getattr(l, k) == v
    l.remove_items()
    for k, v in data.items():
        assert getattr(l, k) == v

    # like and unlike a list
    l.like()
    l.unlike()

    # just test to ensure that iterating over list items works
    l.__iter__()

    # delete entire list
    l.delete_list()


def test_follow_user():
    sean = User('sean')
    sean.follow()
    sean.unfollow()


def test_get_others():
    sean = User('sean')
    for _ in range(2):
        assert all([isinstance(u, User) for u in sean.followers])
        assert all([isinstance(u, User) for u in sean.following])
        assert all([isinstance(u, User) for u in sean.friends])


def test_user_ratings():
    sean = User('sean')
    rating_types = ['movies', 'shows', 'seasons', 'episodes']
    for typ in rating_types:
        assert all([isinstance(r, dict) for r in sean.get_ratings(typ)])
    assert all([isinstance(r, dict) for r in sean.get_ratings('movies', 10)])


def test_user_watchlists():
    sean = User('sean')
    for _ in range(2):
        assert all([isinstance(m, Movie) for m in sean.watchlist_movies])
        assert all([isinstance(s, TVShow) for s in sean.watchlist_shows])


def test_watching():
    sean = User('sean')
    sean.username = 'sean-movie'
    assert isinstance(sean.watching, Movie)
    sean.username = 'sean-episode'
    assert isinstance(sean.watching, TVEpisode)
    sean.username = 'sean-nothing'
    assert sean.watching is None


def test_watched():
    sean = User('sean')
    for _ in range(2):
        assert all([isinstance(m, Movie) for m in sean.watched_movies])
        assert all([isinstance(s, TVShow) for s in sean.watched_shows])


def test_watched_movies_pagination():
    sean = User('sean')
    client = trakt.core.api()
    request_calls = []
    original_request = client.request

    def request(method, uri, data=None):
        request_calls.append((method, uri, data))
        if uri in ('users/sean/watched/movies?page=2&limit=1',
                   'users/sean/watched/movies?limit=1'):
            response = original_request('GET', 'users/sean/watched/movies')
            return deepcopy(response[:1])
        return original_request(method, uri, data)

    client.request = request
    try:
        expected_uri = 'users/sean/watched/movies?page=2&limit=1'
        watched_movies = sean.get_watched_movies(page=2, limit=1)
        assert request_calls[-1] == ('get', expected_uri, None)
        assert len(watched_movies) == 1
        assert all([isinstance(movie, Movie) for movie in watched_movies])

        watched_movies = sean.get_watched_movies(limit=1)
        assert request_calls[-1] == ('get', 'users/sean/watched/movies?limit=1',
                                     None)
        assert len(watched_movies) == 1
        assert all([isinstance(movie, Movie) for movie in watched_movies])

        watched_movies = sean.watched_movies
        assert request_calls[-1] == ('get', 'users/sean/watched/movies', None)
        assert all([isinstance(movie, Movie) for movie in watched_movies])
    finally:
        client.request = original_request


def test_watched_movies_pagination_validation():
    sean = User('sean')

    with pytest.raises(ValueError, match='page must be a positive integer'):
        sean.get_watched_movies(page=0)

    with pytest.raises(ValueError, match='page must be a positive integer'):
        sean.get_watched_movies(page=-1)

    with pytest.raises(ValueError, match='page must be a valid integer'):
        sean.get_watched_movies(page='invalid')

    with pytest.raises(ValueError, match='limit must be a positive integer'):
        sean.get_watched_movies(limit=0)

    with pytest.raises(ValueError, match='limit must be a positive integer'):
        sean.get_watched_movies(limit=-1)

    with pytest.raises(ValueError, match='limit must be a valid integer'):
        sean.get_watched_movies(limit='invalid')


def test_stats():
    sean = User('sean')
    assert isinstance(sean.get_stats(), dict)


def test_liked_lists():
    sean = User('sean')

    lists = sean.get_liked_lists()
    assert lists is None

    lists = sean.get_liked_lists('lists')
    assert isinstance(lists, list)

    lists = sean.get_liked_lists('comments')
    assert isinstance(lists, list)


def test_process_items_ignores_unknown_fields():
    items = [{
        'rank': 1,
        'id': 101,
        'listed_at': '2024-01-01T00:00:00.000Z',
        'type': 'movie',
        'my_rating': 8,
        'movie': {'title': 'TRON', 'year': 1982,
                  'ids': {'trakt': 1, 'slug': 'tron'}},
    }]
    entries = list(PublicList._process_items(items))
    assert len(entries) == 1
    assert entries[0].id == 101
    assert entries[0].data['title'] == 'TRON'
