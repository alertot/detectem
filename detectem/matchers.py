import re

from collections import namedtuple

from parsel import Selector

from detectem.utils import get_response_body

PluginMatch = namedtuple("PluginMatch", "name,version,presence")


def extract_named_group(text, named_group, matchers, return_presence=False):
    """ Return ``named_group`` match from ``text`` reached
        by using a matcher from ``matchers``.

        It also supports matching without a ``named_group`` in a matcher,
        which sets ``presence=True``.

        ``presence`` is only returned if ``return_presence=True``.

    """
    presence = False

    for matcher in matchers:
        if isinstance(matcher, str):
            v = re.search(matcher, text, flags=re.DOTALL)
            if v:
                dict_result = v.groupdict()
                try:
                    return dict_result[named_group]
                except KeyError:
                    if dict_result:
                        # It's other named group matching, discard
                        continue
                    else:
                        # It's a matcher without named_group
                        # but we can't return it until every matcher pass
                        # because a following matcher could have a named group
                        presence = True
        elif callable(matcher):
            v = matcher(text)
            if v:
                return v

    if return_presence and presence:
        return "presence"

    return None


def extract_version(text, *matchers):
    return extract_named_group(text, "version", matchers, return_presence=True)


def extract_name(text, *matchers):
    return extract_named_group(text, "name", matchers)


class UrlMatcher:
    @classmethod
    def get_info(cls, entry, *matchers):
        name = None
        version = None
        presence = False

        for rtype in ["request", "response"]:
            try:
                url = entry[rtype]["url"]
            except KeyError:
                # It could not contain response
                continue

            if not name:
                name = extract_name(url, *matchers)

            if not version:
                version = extract_version(url, *matchers)
                if version:
                    if version == "presence":
                        presence = True
                        version = None

        return PluginMatch(name=name, version=version, presence=presence)


class BodyMatcher:
    @classmethod
    def get_info(cls, entry, *matchers):
        name = None
        version = None
        presence = False
        body = get_response_body(entry)

        name = extract_name(body, *matchers)
        version = extract_version(body, *matchers)
        if version:
            if version == "presence":
                presence = True
                version = None

        return PluginMatch(name=name, version=version, presence=presence)


class HeaderMatcher:
    @classmethod
    def _get_matches(cls, headers, *matchers):
        try:
            for matcher_name, matcher_value in matchers:
                for header in headers:
                    if header["name"] == matcher_name:
                        yield header["value"], matcher_value
        except ValueError:
            raise ValueError("Header matcher value must be a tuple")

    @classmethod
    def get_info(cls, entry, *matchers):
        name = None
        version = None
        presence = False
        headers = entry["response"]["headers"]

        for hstring, hmatcher in cls._get_matches(headers, *matchers):
            # Avoid overriding
            if not name:
                name = extract_name(hstring, hmatcher)

            if not version:
                version = extract_version(hstring, hmatcher)
                if version:
                    if version == "presence":
                        presence = True
                        version = None

        return PluginMatch(name=name, version=version, presence=presence)


class XPathMatcher:
    @classmethod
    def get_info(cls, entry, *matchers):
        name = None
        version = None
        presence = False
        body = get_response_body(entry)
        selector = Selector(text=body)

        for matcher in matchers:
            if len(matcher) == 2:
                xpath, regexp = matcher
            else:
                xpath = matcher[0]
                regexp = None

            value = selector.xpath(xpath).extract_first()
            if not value:
                continue

            if regexp:
                # Avoid overriding
                if not name:
                    name = extract_name(value, regexp)

                version = extract_version(value, regexp)
                if version == "presence":
                    presence = True
                    version = None
                    break
            else:
                presence = True

        return PluginMatch(name=name, version=version, presence=presence)
