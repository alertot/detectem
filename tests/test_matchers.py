import re

import pytest

from detectem.exceptions import NotNamedParameterFound
from detectem.matchers import (
    extract_data, check_presence, extract_version, extract_name,
    UrlMatcher, BodyMatcher, HeaderMatcher, XPathMatcher,
)


def response_text(text):
    return {
        'response': {
            'content': {
                'text': text,
            },
        },
    }


def request_response_url(url):
    return {
        'request': {'url': url},
        'response': {'url': url},
    }


def response_server_header(value):
    return {
        'response': {
            'headers': [{
                'name': 'Server',
                'value': value,
            }],
        },
    }


class TestMatcherHelpers:
    @pytest.mark.parametrize('matcher,result', [
        ('plugin-name', True),
        (lambda v: True, True),
        ('plugin-surname', False),
        (lambda v: False, False),
    ])
    def test_check_presence(self, matcher, result):
        assert check_presence('plugin-name', matcher) == result

    def test_check_presence_arity(self):
        matcher = 'plugin-name'

        assert check_presence('plugin-name', matcher)
        assert check_presence('plugin-name', *[matcher])

    @pytest.mark.parametrize('matcher,result', [
        ('plugin (?P<name>\w+)', 'example'),
        (lambda v: re.findall('plugin (.*)', v)[0], 'example'),
        ('plugin (?P<name>\d+)', None),
        (lambda v: None, None),
    ])
    def test_extract_data(self, matcher, result):
        assert extract_data('plugin example', 'name', matcher) == result

    def test_extract_data_exception(self):
        with pytest.raises(NotNamedParameterFound):
            assert extract_data(
                'plugin example', 'other', 'plugin (?P<name>\w+)'
            )

    def test_extract_data_arity(self):
        matcher = 'plugin (?P<name>\w+)'

        assert extract_data('plugin example', 'name', matcher) == 'example'
        assert extract_data('plugin example', 'name', *[matcher]) == 'example'

    def test_extract_version_uses_version_parameter(self):
        matcher = 'plugin (?P<version>\w+)'
        assert extract_version('plugin example', matcher) == 'example'

    def test_extract_name_uses_name_parameter(self):
        matcher = 'plugin (?P<name>\w+)'
        assert extract_name('plugin example', matcher) == 'example'


class TestUrlMatcher:
    @pytest.fixture
    def version_matcher(self):
        return 'foo-(?P<version>[\d\.]+).js'

    @pytest.fixture
    def name_matcher(self):
        return 'foo-(?P<name>\w+)'

    @pytest.fixture
    def presence_matcher(self):
        return 'foo'

    @pytest.mark.parametrize('entry', [
        {'request': {'url': 'http://domain.tld/foo-1.1.js'}},
        {
            'request': {'url': ''},
            'response': {'url': 'http://domain.tld/foo-1.1.js'},
        }
    ])
    def test_get_version_with_har(self, entry, version_matcher):
        assert UrlMatcher.get_version(entry, version_matcher) == '1.1'

    @pytest.mark.parametrize('url,result', [
        ('http://domain.tld/foo-1.1.js', '1.1'),
        ('http://domain.tld/foo.js', None),
    ])
    def test_get_version(self, url, result, version_matcher):
        entry = request_response_url(url)
        assert UrlMatcher.get_version(entry, version_matcher) == result

    @pytest.mark.parametrize('entry', [
        {'request': {'url': 'http://domain.tld/foo.js'}},
        {
            'request': {'url': ''},
            'response': {'url': 'http://domain.tld/foo.js'},
        }
    ])
    def test_check_presence_with_har(self, entry, presence_matcher):
        assert UrlMatcher.check_presence(entry, presence_matcher)

    @pytest.mark.parametrize('url,result', [
        ('http://domain.tld/foo.js', True),
        ('http://domain.tld/bar.js', False),
    ])
    def test_check_presence(self, url, result, presence_matcher):
        entry = request_response_url(url)
        assert UrlMatcher.check_presence(entry, presence_matcher) == result

    @pytest.mark.parametrize('entry', [
        {'request': {'url': 'http://domain.tld/foo-core-1.1.js'}},
        {
            'request': {'url': ''},
            'response': {'url': 'http://domain.tld/foo-core-1.1.js'},
        }
    ])
    def test_get_module_name_with_har(self, entry, name_matcher):
        assert UrlMatcher.get_module_name(entry, name_matcher) == 'core'

    @pytest.mark.parametrize('url,result', [
        ('http://domain.tld/foo-core-1.1.js', 'core'),
        ('http://domain.tld/foo.js', None),
    ])
    def test_get_module_name(self, url, result, name_matcher):
        entry = request_response_url(url)
        assert UrlMatcher.get_module_name(entry, name_matcher) == result


class TestBodyMatcher:
    @pytest.mark.parametrize('entry,result', [
        (response_text('foo v1.1'), '1.1'),
        (response_text('bar v1.1'), None),
    ])
    def test_get_version(self, entry, result):
        matcher = 'foo v(?P<version>[\d\.]+)'
        assert BodyMatcher.get_version(entry, matcher) == result

    @pytest.mark.parametrize('entry,result', [
        (response_text('foo'), True),
        (response_text('bar'), False),
    ])
    def test_check_presence(self, entry, result):
        matcher = 'foo'
        assert BodyMatcher.check_presence(entry, matcher) == result

    @pytest.mark.parametrize('entry,result', [
        (response_text('foo-core v1.1'), 'core'),
        (response_text('bar-core v1.1'), None),
    ])
    def test_get_module_name(self, entry, result):
        matcher = 'foo-(?P<name>\w+)'
        assert BodyMatcher.get_module_name(entry, matcher) == result


class TestHeaderMatcher:
    @pytest.mark.parametrize('entry,result', [
        (response_server_header('foo v1.1'), '1.1'),
        (response_server_header('bar v1.1'), None),
    ])
    def test_get_version(self, entry, result):
        matcher = ('Server', 'foo v(?P<version>[\d\.]+)')
        assert HeaderMatcher.get_version(entry, matcher) == result

    @pytest.mark.parametrize('entry,result', [
        (response_server_header('foo'), True),
        (response_server_header('bar'), False),
    ])
    def test_check_presence(self, entry, result):
        matcher = ('Server', 'foo')
        assert HeaderMatcher.check_presence(entry, matcher) == result

    @pytest.mark.parametrize('entry,result', [
        (response_server_header('foo-core v1.1'), 'core'),
        (response_server_header('bar-core v1.1'), None),
    ])
    def test_get_module_name(self, entry, result):
        matcher = ('Server', 'foo-(?P<name>\w+)')
        assert HeaderMatcher.get_module_name(entry, matcher) == result


class TestXPathMatcher:
    @pytest.mark.parametrize('entry,result', [
        (response_text('<div>foo v1.1</div>'), '1.1'),
        (response_text('<div>bar v1.1</div>'), None),
    ])
    def test_get_version(self, entry, result):
        matcher = ('//div/text()', 'foo v(?P<version>[\d\.]+)')
        assert XPathMatcher.get_version(entry, matcher) == result

    @pytest.mark.parametrize('entry,result', [
        (response_text('<div>foo</div>'), True),
        (response_text('<div>bar</div>'), False),
    ])
    def test_check_presence(self, entry, result):
        matcher = "//div[contains(text(),'foo')]"
        assert XPathMatcher.check_presence(entry, matcher) == result

    @pytest.mark.parametrize('entry,result', [
        (response_text('<div>foo-core v1.1</div>'), 'core'),
        (response_text('<div>bar-core v1.1</div>'), None),
    ])
    def test_get_module_name(self, entry, result):
        matcher = ('//div/text()', 'foo-(?P<name>\w+)')
        assert XPathMatcher.get_module_name(entry, matcher) == result
