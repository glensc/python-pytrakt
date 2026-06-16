# -*- coding: utf-8 -*-
from unittest.mock import patch

from trakt.movies import Movie
from trakt.sync import Scrobbler


def test_scrobble():
    """test the Scrobbler class's workflow"""
    guardians = Movie('Guardians of the Galaxy', year=2014)
    scrobbler = Scrobbler(guardians, 1.0, '1.0.0', '2015-02-01')
    scrobbler.start()
    scrobbler.update(50.0)
    scrobbler.pause()
    scrobbler.start()
    scrobbler.stop()
    scrobbler.start()
    scrobbler.finish()


def test_scrobbler_context_manager():
    """test the Scrobbler when used as a context manager"""
    guardians = Movie('Guardians of the Galaxy', year=2014)
    with Scrobbler(guardians, 0.0, '1.0.0', '2015-02-01') as scrob:
        for i in range(10):
            scrob.update(i*10)


def test_scrobbler_payload_excludes_app_metadata():
    """scrobble payload must not include undocumented app_version/date fields"""
    import trakt.core
    guardians = Movie('Guardians of the Galaxy', year=2014)

    with patch.object(trakt.core.api(), 'post', return_value=None) as mock_post:
        scrobbler = Scrobbler(guardians, 0.0, '1.0.0', '2015-02-01')
        scrobbler.start(42.0)

    args, kwargs = mock_post.call_args
    assert not kwargs
    assert len(args) >= 2
    payload = args[-1]

    assert isinstance(payload, dict)
    assert payload['progress'] == 42.0
    assert 'app_version' not in payload
    assert 'app_date' not in payload
    assert 'date' not in payload
