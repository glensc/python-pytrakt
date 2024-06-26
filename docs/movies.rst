Movies
------

.. automodule:: trakt.movies
    :members:
    :undoc-members:


Example Usage
^^^^^^^^^^^^^
The trakt.movies module has a handful of functionality for interfacing with
the Movies hosted on Trakt.tv. The module has a few functions which you will
need to be authenticated for. The :func:`dismiss_recommendation` function will
block the specified movie from being shown in your recommended movies.
::

    >>> from trakt.movies import dismiss_recommendation
    >>> dismiss_recommendation('Son of Batman')


This code snippet would prevent Son of Batman from appearing in your recommended
movies list. Following the previous example you can use the
:func:`get_recommended_movies` function to get the list of movies recommended for
the currently authenticated user.
::

    >>> from trakt.movies import get_recommended_movies
    >>> all_movies = get_recommended_movies()
    >>> all_movies
    [<Movie>: 'The Dark Knight', <Movie>: 'WALLE', <Movie>: 'Up', <Movie>: 'Toy Story',...

There are a few properties that belong to the trakt.movies module as well.
::

    >>> from trakt import movies
    >>> movies.genres()
    [Genre(name='Action', slug='action'), Genre(name='Adventure', slug='adventure'),...
    >>> movies.trending_movies()
    [<Movie>: 'The LEGO Movie', <Movie>: 'Non-Stop', <Movie>: 'Frozen', <Movie>: 'RoboCop',...
    >>> movies.updated_movies()
    []

Now to the Movie object. It's pretty straightforward, you provide a title and an
optional year, and you will be returned an interface to that Movie on trakt.tv.
::

    >>> from trakt.movies import Movie
    >>> batman = Movie('Son of Batman', 2014)
    >>> batman.overview
    'Batman learns that he has a violent, unruly pre-teen son with Talia al Ghul named Damian Wayne who is secretly being...
    >>> batman.released
    '2014-04-22'
    >>> batman.genres
    [Genre(name='Action', slug='action'), Genre(name='Adventure', slug='adventure'), Genre(name='Animation', slug='animation')]
    >>> batman.add_to_library()
    >>> batman.mark_as_seen()



