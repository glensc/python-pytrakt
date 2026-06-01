from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from trakt.api import TokenAuth
from trakt.config import AuthConfig
from trakt.errors import OAuthException, OAuthRefreshException


def test_token_refresh_failure_raises_oauth_refresh_exception():
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
    client = Mock()
    client.post.side_effect = OAuthException(response=response)

    auth = TokenAuth(client=client, config=config)

    with pytest.raises(OAuthRefreshException) as exc_info:
        auth.get_token()

    assert exc_info.value.error == 'invalid_grant'
    assert exc_info.value.error_description == 'refresh token is invalid'
    assert auth.TOKEN_UNDER_REFRESH is False
    assert auth.OAUTH_TOKEN_VALID is False
