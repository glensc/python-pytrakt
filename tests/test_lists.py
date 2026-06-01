# -*- coding: utf-8 -*-

from trakt.movies import Movie
from trakt.tv import TVEpisode, TVSeason, TVShow
from trakt.users import PublicList


def test_public_list():
    trakt_id = 1248149
    public_list = PublicList.load(trakt_id)

    assert isinstance(public_list, PublicList)
    assert public_list.name == "MARVEL Cinematic Universe"
    assert public_list.privacy == "public"
    assert public_list.share_link == "https://trakt.tv/lists/1248149"

    # Test iter
    assert len(public_list) == 4

    # enumerate list items
    instancetypes = (Movie, TVShow, TVSeason, TVEpisode)
    assert all([isinstance(k.item, instancetypes) for k in public_list])

    # trakt id is a number
    assert all([isinstance(k.trakt, int) for k in public_list])
