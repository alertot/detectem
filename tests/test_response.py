import pytest

import detectem.utils

from detectem.exceptions import SplashError
from detectem.plugin import Plugin, PluginCollection
from detectem.response import (
    DEFAULT_CHARSET,
    create_lua_script,
    get_charset,
    get_evaljs_error,
    get_response,
    get_valid_har,
    is_url_allowed,
    is_valid_mimetype,
    requests,
)


@pytest.mark.parametrize(
    "url,result",
    [("http://domain.tld/font.ttf", False), ("http://domain.tld/index.html", True)],
)
def test_is_url_allowed(url, result):
    assert is_url_allowed(url) == result


@pytest.mark.parametrize(
    "response,result",
    [
        ({}, True),
        ({"mimeType": "image/gif;charset=utf-8"}, False),
        ({"mimeType": "text/html"}, True),
    ],
)
def test_is_valid_mimetype(response, result):
    assert is_valid_mimetype(response) == result


@pytest.mark.parametrize(
    "response,result",
    [
        ({}, DEFAULT_CHARSET),
        ({"mimeType": ";charset=mycharset"}, "mycharset"),
        ({"otherField": "blabla"}, DEFAULT_CHARSET),
    ],
)
def test_get_charset(response, result):
    assert get_charset(response) == result


def test_create_lua_script():
    class BlaPlugin(Plugin):
        name = "bla"
        matchers = [{"dom": ("bla", "bla.version")}]

    plugins = PluginCollection()
    plugins.add(BlaPlugin())

    script = create_lua_script(plugins)
    assert script

    assert '"name": "bla"' in script
    assert '"check_statement": "bla"' in script
    assert '"version_statement": "bla.version"' in script


def test_get_response(monkeypatch):
    class TestResponse:
        status_code = 200

        def json(self):
            return {"har": {}, "softwares": [], "scripts": {}}

    monkeypatch.setattr(requests, "get", lambda v: TestResponse())
    monkeypatch.setattr(requests, "post", lambda v: v)
    monkeypatch.setattr(detectem.utils, "SETUP_SPLASH", False)

    response = get_response("http://domain.tld", PluginCollection())
    assert response
    assert "har" in response
    assert "softwares" in response


def test_get_response_with_error_status_codes(monkeypatch):
    class TestResponse:
        status_code = 504

        def json(self):
            return {"description": "error 100"}

    monkeypatch.setattr(requests, "get", lambda v: TestResponse())
    monkeypatch.setattr(requests, "post", lambda v: v)
    monkeypatch.setattr(detectem.utils, "SETUP_SPLASH", False)

    with pytest.raises(SplashError):
        get_response("http://domain.tld", PluginCollection())


@pytest.mark.parametrize(
    "har_data,result_len",
    [
        ({}, 0),
        ({"log": {}}, 0),
        ({"log": {"entries": []}}, 0),
        (
            {
                "log": {
                    "entries": [{"request": {"url": "http://fonts.googleapis.com/"}}]
                }
            },
            0,
        ),
        (
            {
                "log": {
                    "entries": [
                        {
                            "request": {"url": "http://domain.tld/"},
                            "response": {"content": {}},
                        }
                    ]
                }
            },
            1,
        ),
        ({"log": {"entries": [{"request": {"url": "http://domain.tld/img.png"}}]}}, 0),
        (
            {
                "log": {
                    "entries": [
                        {
                            "request": {"url": "http://domain.tld"},
                            "response": {
                                "content": {"text": "blab", "mimeType": "image/gif"}
                            },
                        }
                    ]
                }
            },
            0,
        ),
        (
            {
                "log": {
                    "entries": [
                        {
                            "request": {"url": "http://domain.tld/"},
                            "response": {"content": {"text": "blab"}},
                        }
                    ]
                }
            },
            1,
        ),
    ],
)
def test_get_valid_har(har_data, result_len):
    assert len(get_valid_har(har_data)) == result_len


def test_get_evaljs_error():
    json_data = {
        "errors": {
            "evaljs": "ScriptError("
            "{"
            "'js_error_type': 'ReferenceError', "
            "'message': 'JS error: \"ReferenceError: Can\\'t find variable: softwareData\"', "  # noqa: E501
            "'js_error': \"ReferenceError: Can't find variable: softwareData \", "
            "'js_error_message': \"Can't find variable: softwareData\", "
            "'splash_method': 'evaljs', "
            "'type': 'JS_ERROR'"
            "},)"
        }
    }
    message = get_evaljs_error(json_data)
    assert message == 'JS error: "ReferenceError: Can\'t find variable: softwareData"'
