import re

from parsel import Selector


from detectem.exceptions import NotNamedParameterFound


def check_presence(text, *matchers):
    for matcher in matchers:
        if isinstance(matcher, str):
            v = re.search(matcher, text, flags=re.DOTALL)
            if v:
                return True
        elif callable(matcher):
            v = matcher(text)
            if v:
                return True

    return False


def extract_data(text, parameter, *matchers):
    for matcher in matchers:
        if isinstance(matcher, str):
            v = re.search(matcher, text, flags=re.DOTALL)
            if v:
                try:
                    return v.group(parameter)
                except IndexError:
                    raise NotNamedParameterFound(
                        'Parameter %s not found in regexp' %
                        parameter
                    )
        elif callable(matcher):
            v = matcher(text)
            if v:
                return v


def extract_version(text, *matchers):
    return extract_data(text, 'version', *matchers)


def extract_name(text, *matchers):
    return extract_data(text, 'name', *matchers)


class UrlMatcher:
    @classmethod
    def get_version(cls, entry, *matchers):
        for rtype in ['request', 'response']:
            url = entry[rtype]['url']

            version = extract_version(url, *matchers)
            if version:
                return version

    @classmethod
    def check_presence(cls, entry, *matchers):
        for rtype in ['request', 'response']:
            url = entry[rtype]['url']

            if check_presence(url, *matchers):
                return True

        return False

    @classmethod
    def get_module_name(cls, entry, *matchers):
        for rtype in ['request', 'response']:
            url = entry[rtype]['url']

            name = extract_name(url, *matchers)
            if name:
                return name


class BodyMatcher:
    @classmethod
    def get_version(cls, entry, *matchers):
        body = entry['response']['content']['text']

        version = extract_version(body, *matchers)
        if version:
            return version

    @classmethod
    def check_presence(cls, entry, *matchers):
        body = entry['response']['content']['text']

        return check_presence(body, *matchers)

    @classmethod
    def get_module_name(cls, entry, *matchers):
        body = entry['response']['content']['text']

        name = extract_name(body, *matchers)
        if name:
            return name


class HeaderMatcher:
    @classmethod
    def _get_matches(cls, headers, *matchers):
        for matcher_name, matcher_value in matchers:
            for header in headers:
                if header['name'] == matcher_name:
                    yield header['value'], matcher_value

    @classmethod
    def get_version(cls, entry, *matchers):
        headers = entry['response']['headers']

        for hstring, hmatcher in cls._get_matches(headers, *matchers):
            version = extract_version(hstring, hmatcher)
            if version:
                return version

    @classmethod
    def check_presence(cls, entry, *matchers):
        headers = entry['response']['headers']

        for hstring, hmatcher in cls._get_matches(headers, *matchers):
            if check_presence(hstring, hmatcher):
                return True

        return False

    @classmethod
    def get_module_name(cls, entry, *matchers):
        headers = entry['response']['headers']

        for hstring, hmatcher in cls._get_matches(headers, *matchers):
            name = extract_name(hstring, hmatcher)
            if name:
                return name


class XPathMatcher:
    @classmethod
    def get_version(cls, entry, *matchers):
        body = entry['response']['content']['text']
        selector = Selector(text=body)

        for xpath, regexp in matchers:
            value = selector.xpath(xpath).extract_first()
            if not value:
                continue

            version = extract_version(value, regexp)
            if version:
                return version

    @classmethod
    def check_presence(cls, entry, *matchers):
        body = entry['response']['content']['text']
        selector = Selector(text=body)

        for xpath in matchers:
            sel = selector.xpath(xpath)
            if sel:
                return True

        return False

    @classmethod
    def get_module_name(cls, entry, *matchers):
        body = entry['response']['content']['text']
        selector = Selector(text=body)

        for xpath, regexp in matchers:
            value = selector.xpath(xpath).extract_first()
            if not value:
                continue

            name = extract_name(value, regexp)
            if name:
                return name
