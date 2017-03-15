import pytest
import json

import detectem.utils
from detectem.response import (
    is_url_allowed, get_charset, create_lua_script,
    get_valid_har, get_response, DEFAULT_CHARSET
)
from detectem.exceptions import SplashError
from detectem.response import requests


@pytest.mark.parametrize("url,blacklist,result", [
    ('http://domain.tld/black', ['black'], False),
    ('http://domain.tld/black', ['white'], True),
])
def test_is_url_allowed(url, blacklist, result):
    assert is_url_allowed(url, blacklist) == result


@pytest.mark.parametrize("response,result", [
    ({}, DEFAULT_CHARSET),
    ({'mimeType': ';charset=mycharset'}, 'mycharset'),
    ({'otherField': 'blabla'}, DEFAULT_CHARSET),
])
def test_get_charset(response, result):
    assert get_charset(response) == result


def test_create_lua_script():
    class BlaPlugin():
        name = 'bla'
        js_matchers = [{'check': 'bla', 'version': 'bla.version'}]

    script = create_lua_script(plugins=[BlaPlugin()])
    assert script

    js_data = json.dumps(BlaPlugin.js_matchers)
    assert js_data in script


def test_get_response(monkeypatch):
    class TestResponse():
        status_code = 200

        def json(self):
            return {'har': {}, 'softwares': []}

    monkeypatch.setattr(requests, 'get', lambda v: TestResponse())
    monkeypatch.setattr(requests, 'post', lambda v: v)
    monkeypatch.setattr(detectem.utils, 'SETUP_SPLASH', False)

    response = get_response('http://domain.tld', {})
    assert response
    assert 'har' in response
    assert 'softwares' in response


def test_get_response_with_error_status_codes(monkeypatch):
    class TestResponse():
        status_code = 504

        def json(self):
            return {'description': 'error 100'}

    monkeypatch.setattr(requests, 'get', lambda v: TestResponse())
    monkeypatch.setattr(requests, 'post', lambda v: v)
    monkeypatch.setattr(detectem.utils, 'SETUP_SPLASH', False)

    with pytest.raises(SplashError):
        get_response('http://domain.tld', {})


@pytest.mark.parametrize("har_data,result_len", [
    ({}, 0),
    ({'log': {}}, 0),
    ({'log': {'entries': []}}, 0),
    (
        {
            'log': {
                'entries': [
                    {'request': {'url': 'http://fonts.googleapis.com/'}}
                ]
            }
        },
        0
    ),
    (
        {
            'log': {
                'entries': [
                    {
                        'request': {'url': 'http://domain.tld/'},
                        'response': {'content': {}}
                    }
                ]
            }
        },
        0
    ),
    (
        {
            'log': {
                'entries': [
                    {
                        'request': {'url': 'http://domain.tld/'},
                        'response': {'content': {'text': 'blab'}}
                    }
                ]
            }
        },
        1
    ),
])
def test_get_valid_har(har_data, result_len):
    assert len(get_valid_har(har_data)) == result_len
