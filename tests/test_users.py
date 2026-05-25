# -*- coding: utf-8 -*-
from trakt.movies import Movie
from trakt.people import Person
from trakt.tv import TVEpisode, TVSeason, TVShow
from trakt.users import (Request, User, UserList, get_all_requests,
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

    movie_page = sean.collection('movies', page=1, limit=250)
    show_page = sean.collection('shows', page=1, limit=250)
    assert movie_page
    assert show_page
    assert all(['movie' in item for item in movie_page])
    assert all(['show' in item for item in show_page])
    assert sean.collection('movies', page=2, limit=250) == []
    assert sean.collection('shows', page=2, limit=250) == []


def test_user_list():
    sean = User('sean')
    assert all([isinstance(user_list, UserList) for user_list in sean.lists])

    data = dict(name='Star Wars in machete order',
                description='Some descriptive text',
                privacy='public',
                display_numbers=True)
    # create list
    user_list = UserList.create(creator=sean.username, **data)
    for k, v in data.items():
        assert getattr(user_list, k) == v

    # get list
    user_list = UserList.get(data['name'], sean.username)
    assert len(list(user_list)) == 5

    user_list = sean.get_list(data['name'])
    for k, v in data.items():
        assert getattr(user_list, k) == v
    assert len(list(user_list)) == 5

    # enumerate list items
    instancetypes = (Movie, TVShow, TVSeason, TVEpisode, Person)
    assert all([isinstance(k, instancetypes) for k in user_list])

    # PUT to add and remove items from list
    user_list.add_items()
    for k, v in data.items():
        assert getattr(user_list, k) == v
    user_list.remove_items()
    for k, v in data.items():
        assert getattr(user_list, k) == v

    # like and unlike a list
    user_list.like()
    user_list.unlike()

    # just test to ensure that iterating over list items works
    user_list.__iter__()

    # delete entire list
    user_list.delete_list()


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

    movie_page = sean.watchlist('movies', page=1, limit=250)
    show_page = sean.watchlist('shows', page=1, limit=250)
    assert movie_page
    assert show_page
    assert all([item['type'] == 'movie' for item in movie_page])
    assert all([item['type'] == 'show' for item in show_page])
    assert sean.watchlist('movies', page=2, limit=250) == []
    assert sean.watchlist('shows', page=2, limit=250) == []


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

    movie_page = sean.watched('movies', page=1, limit=250)
    show_page = sean.watched('shows', page=1, limit=250)
    assert all(['movie' in item for item in movie_page])
    assert all(['show' in item for item in show_page])
    assert sean.watched('movies', page=2, limit=250) == []
    assert sean.watched('shows', page=2, limit=250) == []


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
