# -*- coding: utf-8 -*-
"""unit tests for the trakt.utils module"""
from datetime import datetime

from trakt.utils import (airs_date, build_uri, extract_ids, now, slugify,
                         timestamp)


def test_slugify():
    """Verify that the slugify function works as expected"""
    test_data = [
        ('IM AN ALL CAPS STRING', 'im-an-all-caps-string'),
        ('IM A BAD A$$ STRING!@', 'im-a-bad-a-string'),
        (' LOOK AT MY WHITESPACE   ', 'look-at-my-whitespace'),
        ("Marvel's Agents of S.H.I.E.L.D.", 'marvel-s-agents-of-s-h-i-e-l-d'),
        ('Naruto Shippūden', 'naruto-shippuden'),
        ('Re:ZERO -Starting Life in Another World-', 're-zero-starting-life-in-another-world'),
        ('So I’m a Spider, So What?', 'so-i-m-a-spider-so-what'),
    ]

    for inp, expected in test_data:
        observed = slugify(inp)
        assert observed == expected


def test_airs_date():
    """verify that the airs_date function works as expected"""
    stamps = ['2015-02-01T05:30:00.000-08:00Z',
              '2015-02-01T05:30:00.000Z']
    for timestamp in stamps:
        output = airs_date(timestamp)
        assert output.year == 2015
        assert output.month == 2
        assert output.day == 1
        assert output.hour == 5
        assert output.minute == 30
        assert output.second == 0


def test_now():
    """verify that the now timestamp generator works as expected"""
    result = now()
    dates = result.split('-')
    assert len(dates) == 3
    assert len(dates[0]) == 4  # year
    assert len(dates[1]) == 2  # month
    assert len(dates[2]) == 2  # day


def test_timestamp():
    """verify that the trakt timestamp converter works as expected"""
    meow = datetime.now()
    result = timestamp(meow)
    assert result.startswith(str(meow.year))
    assert result.endswith('.000Z')


def test_extract_ids():
    """verify that id dicts can be correctly extracted"""
    ids = dict(trakt=443, tvdb=4851180, imdb='tt3500614', tmdb=988123,
               tvrage=None)
    input_dict = {'ids': ids}
    result = extract_ids(input_dict)
    assert result == ids


def test_build_uri():
    """verify that uri query params are appended correctly"""
    assert build_uri('users/{user}/watched/movies', user='sean') == \
        'users/sean/watched/movies'
    assert build_uri('shows/popular', page=2, limit=10) == \
        'shows/popular?page=2&limit=10'
    assert build_uri('shows/popular', extended='full') == \
        'shows/popular?extended=full'
    assert build_uri('shows/popular', page=2, extended='full') == \
        'shows/popular?page=2&extended=full'
    assert build_uri('shows/popular?sort=rank', page=2) == \
        'shows/popular?sort=rank&page=2'


def test_build_uri_pagination_validation():
    """verify that pagination params are validated by the helper"""
    from pytest import raises

    with raises(ValueError, match='page must be a positive integer'):
        build_uri('shows/popular', page=0)

    with raises(ValueError, match='limit must be a valid integer'):
        build_uri('shows/popular', limit='invalid')


def test_validate_pagination_param_rejects_bools_and_fractional_floats():
    """verify pagination validation rejects values that should not coerce"""
    from pytest import raises

    with raises(ValueError, match='page must be a valid integer'):
        build_uri('shows/popular', page=True)

    with raises(ValueError, match='limit must be a valid integer'):
        build_uri('shows/popular', limit=1.5)
