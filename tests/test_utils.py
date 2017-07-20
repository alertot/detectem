import re

import pytest

from detectem.utils import check_presence, extract_version, extract_from_headers
from detectem.exceptions import NotNamedParameterFound


@pytest.mark.parametrize("matcher", [
    ("version is v(?P<version>[0-9\.]+)"),
    (lambda v: re.findall('version is v(.*)', v)[0]),
])
def test_extract_version_with_matching_matcher(matcher):
    assert extract_version('the version is v1.0.0', [matcher]) == '1.0.0'


@pytest.mark.parametrize("matcher", [
    ("version is v(?P<version>[a-d]+)"),
    (lambda v: None),
])
def test_extract_version_with_not_matching_matcher(matcher):
    assert not extract_version('the version is v1.0.0', [matcher])


def test_extract_version_with_invalid_matcher():
    with pytest.raises(NotNamedParameterFound):
        assert extract_version('the version is v1.0.0', ["version is v([0-9\.]+)"])


@pytest.mark.parametrize("headers, matchers", [
    ([], []),
    ([{'name': 'Header', 'value': 'software v1.1.1'}], []),
])
def test_extract_from_headers_version_not_matching(headers, matchers):
    assert not extract_from_headers(headers, matchers, extract_version)


def test_extract_from_headers_matching_version():
    headers = [{'name': 'Header', 'value': 'software v1.1.1'}]
    matchers = [('Header', 'software v(?P<version>.*)')]

    assert extract_from_headers(headers, matchers, extract_version) == '1.1.1'


@pytest.mark.parametrize("headers, matchers", [
    ([], []),
    ([{'name': 'Header', 'value': 'awesome software'}], []),
])
def test_extract_from_headers_value_not_present(headers, matchers):
    assert not extract_from_headers(headers, matchers, check_presence)


def test_extract_from_headers_value_is_present():
    headers = [{'name': 'Header', 'value': 'awesome software'}]
    matchers = [('Header', '.*awesome software.*')]

    assert extract_from_headers(headers, matchers, check_presence)
