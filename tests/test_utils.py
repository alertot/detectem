import re

import pytest

from detectem.utils import extract_version, extract_version_from_headers
from detectem.exceptions import NotVersionNamedParameterFound


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
    with pytest.raises(NotVersionNamedParameterFound):
        assert extract_version('the version is v1.0.0', ["version is v([0-9\.]+)"])


@pytest.mark.parametrize("headers, matchers", [
    ([], []),
    ([{'name': 'Header', 'value': 'software v1.1.1'}], []),
])
def test_extract_version_from_headers_not_matching(headers, matchers):
    assert not extract_version_from_headers(headers, matchers)


def test_extract_version_from_headers_matching():
    headers = [{'name': 'Header', 'value': 'software v1.1.1'}]
    matchers = [('Header', 'software v(?P<version>.*)')]

    assert extract_version_from_headers(headers, matchers) == '1.1.1'
