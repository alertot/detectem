import re

import pytest

from detectem.matchers import (
    BodyMatcher,
    HeaderMatcher,
    UrlMatcher,
    XPathMatcher,
    extract_name,
    extract_named_group,
    extract_version,
)
from tests import create_pm


def res_text(text):
    return {"response": {"content": {"text": text}}}


def req_res_url(url):
    return {"request": {"url": url}, "response": {"url": url}}


def res_server_header(value):
    return {"response": {"headers": [{"name": "Server", "value": value}]}}


class TestMatcherHelpers:
    @pytest.mark.parametrize(
        "matcher,result",
        [
            (r"plugin (?P<target>\w+)", "example"),
            (r"plugin (?P<target>\d+)", None),
            (r"plugin (?P<other>\w+)", None),
            (lambda v: re.findall("plugin (.*)", v)[0], "example"),
            (lambda v: None, None),
        ],
    )
    def test_extract_named_group(self, matcher, result):
        assert extract_named_group("plugin example", "target", [matcher]) == result

    def test_extract_named_group_with_presence(self):
        matcher = "plugin example"

        assert extract_named_group("plugin example", "target", [matcher]) is None
        assert (
            extract_named_group(
                "plugin example", "target", [matcher], return_presence=True
            )
            == "presence"
        )

    def test_extract_named_group_with_different_named_group_and_presence(self):
        matcher = r"plugin (?P<notarget>\w+)"

        assert (
            extract_named_group(
                "plugin example", "target", [matcher], return_presence=True
            )
            is None
        )

    def test_extract_version_uses_version_parameter(self):
        matcher = r"plugin (?P<version>\w+)"
        assert extract_version("plugin example", matcher) == "example"

    def test_extract_name_uses_name_parameter(self):
        matcher = r"plugin (?P<name>\w+)"
        assert extract_name("plugin example", matcher) == "example"


class TestMatchers:
    version_re = r"foo-(?P<version>[\d\.]+)"
    presence_re = "foo"
    name_re = r"foo-(?P<name>\w+)"

    @pytest.mark.parametrize(
        "matcher_class,entry,matcher,version",
        [
            (UrlMatcher, req_res_url("http://d.tld/foo-1.1"), version_re, "1.1"),
            (UrlMatcher, req_res_url("http://d.tld/foo"), version_re, None),
            (BodyMatcher, res_text("foo-1.1"), version_re, "1.1"),
            (BodyMatcher, res_text("bar-1.1"), version_re, None),
            (
                HeaderMatcher,
                res_server_header("foo-1.1"),
                ("Server", version_re),
                "1.1",
            ),
            (HeaderMatcher, res_server_header("bar-1.1"), ("Server", version_re), None),
            (
                XPathMatcher,
                res_text("<a>foo-1.1</a>"),
                ("//a/text()", version_re),
                "1.1",
            ),
            (
                XPathMatcher,
                res_text("<a>bar-1.1</a>"),
                ("//a/text()", version_re),
                None,
            ),
        ],
    )  # yapf: disable
    def test_get_version(self, matcher_class, entry, matcher, version):
        assert matcher_class.get_info(entry, matcher) == create_pm(version=version)

    @pytest.mark.parametrize(
        "matcher_class,entry,matcher,presence",
        [
            (UrlMatcher, req_res_url("http://d.tld/foo"), presence_re, True),
            (UrlMatcher, req_res_url("http://d.tld/bar"), presence_re, False),
            (BodyMatcher, res_text("foo"), presence_re, True),
            (BodyMatcher, res_text("bar"), presence_re, False),
            (HeaderMatcher, res_server_header("foo"), ("Server", presence_re), True),
            (HeaderMatcher, res_server_header("bar"), ("Server", presence_re), False),
            (XPathMatcher, res_text("<a>foo</a>"), ("//a/text()", presence_re), True),
            (XPathMatcher, res_text("<a>bar</a>"), ("//a/text()", presence_re), False),
        ],
    )  # yapf: disable
    def test_get_presence(self, matcher_class, entry, matcher, presence):
        assert matcher_class.get_info(entry, matcher) == create_pm(presence=presence)

    @pytest.mark.parametrize(
        "matcher_class,entry,matcher,name",
        [
            (UrlMatcher, req_res_url("http://d.tld/foo-core"), name_re, "core"),
            (UrlMatcher, req_res_url("http://d.tld/bar-core"), name_re, None),
            (BodyMatcher, res_text("foo-core"), name_re, "core"),
            (BodyMatcher, res_text("bar-core"), name_re, None),
            (HeaderMatcher, res_server_header("foo-core"), ("Server", name_re), "core"),
            (HeaderMatcher, res_server_header("bar-core"), ("Server", name_re), None),
            (
                XPathMatcher,
                res_text("<a>foo-core</a>"),
                ("//a/text()", name_re),
                "core",
            ),
            (XPathMatcher, res_text("<a>bar-core</a>"), ("//a/text()", name_re), None),
        ],
    )  # yapf: disable
    def test_get_name(self, matcher_class, entry, matcher, name):
        assert matcher_class.get_info(entry, matcher) == create_pm(name=name)


class TestUrlMatcher:
    @pytest.mark.parametrize(
        "entry",
        [
            {"request": {"url": "http://d.tld/foo-1.1"}},
            {"request": {"url": ""}, "response": {"url": "http://d.tld/foo-1.1"}},
        ],
    )
    def test_get_version_with_har(self, entry):
        version_re = r"foo-(?P<version>[\d\.]+)"
        assert UrlMatcher.get_info(entry, version_re) == create_pm(version="1.1")
