# -*- coding: utf-8 -*-
"""unit tests to define behavior of custom exception types"""
from unittest.mock import MagicMock

from trakt.errors import (BadRequestException, ConflictException,
                          ForbiddenException, NotFoundException,
                          OAuthException, OAuthRefreshException,
                          ProcessException, RateLimitException,
                          TraktException, TraktInternalException,
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


def test_oauth_refresh_exception_default_str():
    texc = OAuthRefreshException()
    assert str(texc) == 'Unauthorized - OAuth token refresh failed'


def test_oauth_refresh_exception_from_response_json():
    response = MagicMock()
    response.json.return_value = {'error': 'invalid_grant', 'error_description': 'Token has expired'}
    texc = OAuthRefreshException(response=response)
    assert texc.error == 'invalid_grant'
    assert texc.error_description == 'Token has expired'
    assert str(texc) == 'Unauthorized - OAuth token refresh failed: invalid_grant - Token has expired'


def test_oauth_refresh_exception_explicit_args_override_response():
    response = MagicMock()
    response.json.return_value = {'error': 'from_response', 'error_description': 'from_response_desc'}
    texc = OAuthRefreshException(response=response, error='explicit_error', error_description='explicit_desc')
    assert texc.error == 'explicit_error'
    assert texc.error_description == 'explicit_desc'


def test_oauth_refresh_exception_no_response():
    texc = OAuthRefreshException(response=None)
    assert texc.error is None
    assert texc.error_description is None
    assert str(texc) == 'Unauthorized - OAuth token refresh failed'


def test_oauth_refresh_exception_json_raises():
    response = MagicMock()
    response.json.side_effect = ValueError('not json')
    texc = OAuthRefreshException(response=response)
    assert texc.error is None
    assert texc.error_description is None


def test_oauth_refresh_exception_error_only_str():
    texc = OAuthRefreshException(error='invalid_client')
    assert str(texc) == 'Unauthorized - OAuth token refresh failed: invalid_client'


def test_oauth_refresh_exception_cause():
    cause = RuntimeError('original')
    texc = OAuthRefreshException(cause=cause)
    assert texc.cause is cause
