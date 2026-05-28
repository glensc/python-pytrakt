# -*- coding: utf-8 -*-
"""unit tests to define behavior of custom exception types"""
from unittest.mock import Mock

from trakt.errors import (BadRequestException, ConflictException,
                          ForbiddenException, NotFoundException,
                          OAuthException, OAuthRefreshException,
                          ProcessException, RateLimitException, TraktException,
                          TraktInternalException,
                          TraktUnavailable)


def test_trakt_exception():
    texc = TraktException()
    assert texc.http_code is None
    assert texc.message is None


def test_400_exception():
    texc = BadRequestException()
    assert texc.http_code == 400
    assert texc.message == "Bad Request - request couldn't be parsed"
    assert str(texc) == texc.message


def test_401_exception():
    texc = OAuthException()
    assert texc.http_code == 401
    assert texc.message == 'Unauthorized - OAuth must be provided'
    assert str(texc) == texc.message


def test_oauth_refresh_exception_default_string():
    texc = OAuthRefreshException()
    assert texc.error is None
    assert texc.error_description is None
    assert str(texc) == 'Unauthorized - OAuth token refresh failed'


def test_oauth_refresh_exception_parses_response_data():
    response = Mock()
    response.json.return_value = {
        'error': 'invalid_grant',
        'error_description': 'refresh token is invalid',
    }

    texc = OAuthRefreshException(response=response)

    assert texc.error == 'invalid_grant'
    assert texc.error_description == 'refresh token is invalid'
    assert (
        str(texc) ==
        'Unauthorized - OAuth token refresh failed: invalid_grant - '
        'refresh token is invalid'
    )


def test_oauth_refresh_exception_explicit_values_override_response_data():
    response = Mock()
    response.json.return_value = {
        'error': 'invalid_grant',
        'error_description': 'refresh token is invalid',
    }

    texc = OAuthRefreshException(
        response=response,
        error='invalid_client',
        error_description='client authentication failed',
        cause='unit-test-cause',
    )

    assert texc.error == 'invalid_client'
    assert texc.error_description == 'client authentication failed'
    assert texc.cause == 'unit-test-cause'


def test_oauth_refresh_exception_handles_missing_or_invalid_response_json():
    invalid_response = OAuthRefreshException(response=object())
    assert invalid_response.error is None
    assert invalid_response.error_description is None
    assert str(invalid_response) == 'Unauthorized - OAuth token refresh failed'

    bad_response = Mock()
    bad_response.json.side_effect = ValueError('bad json')
    texc = OAuthRefreshException(response=bad_response)
    assert texc.error is None
    assert texc.error_description is None
    assert str(texc) == 'Unauthorized - OAuth token refresh failed'


def test_oauth_refresh_exception_string_for_error_only():
    texc = OAuthRefreshException(error='invalid_grant')
    assert (
        str(texc) ==
        'Unauthorized - OAuth token refresh failed: invalid_grant'
    )


def test_403_exception():
    texc = ForbiddenException()
    assert texc.http_code == 403
    assert texc.message == 'Forbidden - invalid API key or unapproved app'
    assert str(texc) == texc.message


def test_404_exception():
    texc = NotFoundException()
    assert texc.http_code == 404
    assert texc.message == 'Not Found - method exists, but no record found'
    assert str(texc) == texc.message


def test_409_exception():
    texc = ConflictException()
    assert texc.http_code == 409
    assert texc.message == 'Conflict - resource already created'
    assert str(texc) == texc.message


def test_422_exception():
    texc = ProcessException()
    assert texc.http_code == 422
    assert texc.message == 'Unprocessable Entity - validation errors'
    assert str(texc) == texc.message


def test_429_exception():
    texc = RateLimitException()
    assert texc.http_code == 429
    assert texc.message == 'Rate Limit Exceeded'
    assert str(texc) == texc.message


def test_500_exception():
    texc = TraktInternalException()
    assert texc.http_code == 500
    assert texc.message == 'Internal Server Error'
    assert str(texc) == texc.message


def test_503_exception():
    texc = TraktUnavailable()
    assert texc.http_code == 503
    assert texc.message == 'Trakt Unavailable - server overloaded'
    assert str(texc) == texc.message
