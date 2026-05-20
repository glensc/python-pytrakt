from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from trakt.api import HttpClient
from trakt.api import TokenAuth
from trakt.config import AuthConfig
from trakt.core import api
from trakt.errors import OAuthException, OAuthRefreshException
from trakt.tv import TVShow


def test_api_singleton():
    """Test that api() returns the same HttpClient instance when called multiple times."""
    api1 = api()
    api2 = api()
    assert isinstance(api1, HttpClient), "api() should return an HttpClient instance"
    assert api1 == api2, "Multiple calls to api() should return the same instance"


def test_tvshow_properties():
    show = TVShow("Game of Thrones")
    assert show.title == "Game of Thrones"
    assert show.certification == "TV-MA"


def test_token_refresh_failure_raises_dedicated_exception():
    config = AuthConfig('missing.json').update(
        CLIENT_ID='client-id',
        CLIENT_SECRET='client-secret',
        OAUTH_TOKEN='stale-token',
        OAUTH_REFRESH='refresh-token',
        OAUTH_EXPIRES_AT=int((datetime.now(tz=timezone.utc) - timedelta(minutes=1)).timestamp()),
    )
    response = Mock()
    response.json.return_value = {
        'error': 'invalid_grant',
        'error_description': 'refresh token is invalid',
    }
    response.text = 'refresh token is invalid'
    client = Mock()
    client.post.side_effect = OAuthException(response=response)

    auth = TokenAuth(client=client, config=config)

    with pytest.raises(OAuthRefreshException) as exc_info:
        auth.get_token()

    assert exc_info.value.error == 'invalid_grant'
    assert exc_info.value.error_description == 'refresh token is invalid'
    assert auth.TOKEN_UNDER_REFRESH is False
    assert auth.OAUTH_TOKEN_VALID is False
