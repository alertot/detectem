import logging
import urllib.parse

from collections import defaultdict
from distutils.version import LooseVersion

from detectem.utils import (
    extract_version, extract_name, extract_from_headers,
    get_most_complete_version, check_presence
)
from detectem.settings import (
    VERSION_TYPE, INDICATOR_TYPE, HINT_TYPE,
    MAIN_ENTRY, RESOURCE_ENTRY, INLINE_SCRIPT_ENTRY
)

logger = logging.getLogger('detectem')


class Result():
    def __init__(
        self, name, version=None, homepage=None, from_url=None, type=VERSION_TYPE
    ):
        self.name = name
        self.type = type
        self.version = version
        self.homepage = homepage
        self.from_url = from_url

    def __hash__(self):
        return hash((self.name, self.version, self.type))

    def __eq__(self, o):
        def to_tuple(rt):
            return (rt.name, rt.version, rt.type)
        return to_tuple(self) == to_tuple(o)

    def __lt__(self, o):
        def to_tuple(rt):
            return (rt.name, LooseVersion(rt.version or '0'), rt.type)
        return to_tuple(self) < to_tuple(o)

    def __repr__(self):
        return str({'name': self.name, 'version': self.version, 'type': self.type})


class ResultCollection():

    def __init__(self):
        self._results = defaultdict(list)

    def add_result(self, rt):
        self._results[rt.name].append(rt)

    def _normalize_results(self):
        norm_results = defaultdict(list)

        for p_name, p_results in self._results.items():
            rdict = defaultdict(set)
            for rt in p_results:
                rdict[rt.type].add(rt)

            p_list = []
            if VERSION_TYPE in rdict:
                p_list = list(rdict[VERSION_TYPE])
                assert len(p_list) >= 1
            elif INDICATOR_TYPE in rdict:
                p_list = list(rdict[INDICATOR_TYPE])
                assert len(p_list) == 1
            elif HINT_TYPE in rdict:
                p_list = list(rdict[HINT_TYPE])
                assert len(p_list) == 1

            norm_results[p_name] = p_list

        return norm_results

    def get_results(self, normalize=True):
        results = self._normalize_results() if normalize else self._results
        return [rt for p_results in results.values() for rt in p_results]


class Detector():
    def __init__(self, response, plugins, requested_url):
        self.requested_url = requested_url
        self.har = self._prepare_har(response)

        self._softwares_from_splash = response['softwares']
        self._plugins = plugins
        self._results = ResultCollection()

    def _prepare_har(self, response):
        har = response.get('har', [])
        if har:
            self._mark_main_entry(har)
        for script in response.get('scripts', []):
            har.append(self._script_to_har_entry(script))
        return har

    def _mark_main_entry(self, entries):
        for entry in entries:
            self._set_entry_type(entry, RESOURCE_ENTRY)

        def get_url(entry):
            return entry['request']['url']

        def get_location(entry):
            headers = entry['response'].get('headers', [])
            for header in headers:
                if header['name'] == 'Location':
                    return header['value']
            return None

        main_entry = entries[0]
        main_location = get_location(main_entry)
        if not main_location:
            self._set_entry_type(main_entry, MAIN_ENTRY)
            return
        main_url = urllib.parse.urljoin(get_url(main_entry), main_location)

        for entry in entries[1:]:
            url = get_url(entry)
            if url == main_url:
                self._set_entry_type(entry, MAIN_ENTRY)
                break
        else:
            self._set_entry_type(main_entry, MAIN_ENTRY)

    def _script_to_har_entry(self, script):
        entry = {
            'request': {
                'url': self.requested_url,
            },
            'response': {
                'url': self.requested_url,
                'content': {
                    'text': script
                }
            }
        }
        self._set_entry_type(entry, INLINE_SCRIPT_ENTRY)
        return entry

    @staticmethod
    def _set_entry_type(entry, entry_type):
        entry.setdefault('detectem', {})['type'] = entry_type

    @staticmethod
    def _get_entry_type(entry):
        return entry['detectem']['type']

    @staticmethod
    def get_url(entry):
        """ Return URL from response if it was received otherwise requested URL """
        if 'response' in entry:
            return entry['response']['url']

        return entry['request']['url']

    def get_hints(self, plugin, entry):
        """ Get plugins hints from `plugin` on `entry`.

        Plugins hints return `Result` or `None`.

        """
        hints = []

        for hint_name in getattr(plugin, 'hints', []):
            hint_plugin = self._plugins.get(hint_name)
            if hint_plugin:
                hint_result = Result(
                    name=hint_plugin.name,
                    homepage=hint_plugin.homepage,
                    from_url=self.requested_url,
                    type=HINT_TYPE
                )
                hints.append(hint_result)
                logger.debug(
                    '%(pname)s & hint %(hname)s detected',
                    {'pname': plugin.name, 'hname': hint_result.name}
                )
            else:
                logger.error(
                    '%(pname)s hints an invalid plugin: %(hname)s',
                    {'pname': plugin.name, 'hname': hint_name}
                )

        return hints

    def process_from_splash(self):
        for software in self._softwares_from_splash:
            plugin = self._plugins.get(software['name'])
            self._results.add_result(
                Result(
                    name=plugin.name,
                    version=software['version'],
                    homepage=plugin.homepage,
                    from_url=self.requested_url,
                )
            )

    def process_har(self):
        """ Detect plugins present in the page.

        First, start with version plugins, then software from Splash
        and finish with indicators.
        In each phase try to detect plugin hints in already detected plugins.

        """
        hints = []

        version_plugins = self._plugins.with_version_matchers()
        indicator_plugins = self._plugins.with_indicator_matchers()

        for entry in self.har:
            for plugin in version_plugins:
                version = self.get_plugin_version(plugin, entry)
                if version:
                    # Name could be different than plugin name in modular plugins
                    name = self.get_plugin_name(plugin, entry)
                    self._results.add_result(
                        Result(
                            name=name,
                            version=version,
                            homepage=plugin.homepage,
                            from_url=self.get_url(entry)
                        )
                    )
                    hints += self.get_hints(plugin, entry)

            for plugin in indicator_plugins:
                is_present = self.check_indicator_presence(plugin, entry)
                if is_present:
                    self._results.add_result(
                        Result(
                            name=plugin.name,
                            homepage=plugin.homepage,
                            from_url=self.get_url(entry),
                            type=INDICATOR_TYPE
                        )
                    )
                    hints += self.get_hints(plugin, entry)

        for hint in hints:
            self._results.add_result(hint)

    def get_results(self, metadata=False):
        """ Return results of the analysis. """
        results_data = []

        self.process_har()
        self.process_from_splash()

        for rt in sorted(self._results.get_results()):
            rdict = {'name': rt.name}
            if rt.version:
                rdict['version'] = rt.version

            if metadata:
                rdict['homepage'] = rt.homepage
                rdict['type'] = rt.type
                rdict['from_url'] = rt.from_url

            results_data.append(rdict)

        return results_data

    def _get_matchers_for_entry(self, source, plugin, entry):
        grouped_matchers = plugin.get_grouped_matchers(source)

        def remove_group(group):
            if group in grouped_matchers:
                del grouped_matchers[group]

        if self._get_entry_type(entry) == MAIN_ENTRY:
            remove_group('body')
            remove_group('url')
        else:
            remove_group('header')

        return grouped_matchers

    def get_values_from_matchers(self, entry, matchers, extraction_function):
        values = []

        for key, matchers in matchers.items():
            method = getattr(self, 'from_{}'.format(key))
            value = method(entry, matchers, extraction_function)
            if value:
                values.append(value)

        return values

    def get_plugin_version(self, plugin, entry):
        """ Return version after applying every plugin matcher. """
        grouped_matchers = self._get_matchers_for_entry(
            'matchers', plugin, entry
        )
        versions = self.get_values_from_matchers(
            entry, grouped_matchers, extract_version
        )
        return get_most_complete_version(versions)

    def get_plugin_name(self, plugin, entry):
        if not plugin.is_modular:
            return plugin.name

        grouped_matchers = self._get_matchers_for_entry(
            'modular_matchers', plugin, entry
        )
        module_name = self.get_values_from_matchers(
            entry, grouped_matchers, extract_name
        )

        if module_name:
            name = '{}-{}'.format(plugin.name, module_name[0])
        else:
            name = plugin.name

        return name

    def check_indicator_presence(self, plugin, entry):
        grouped_matchers = self._get_matchers_for_entry(
            'indicators', plugin, entry
        )
        presence_list = self.get_values_from_matchers(
            entry, grouped_matchers, check_presence
        )
        return any(presence_list)

    @staticmethod
    def from_url(entry, matchers, extraction_function):
        """ Return version from request or response url.
        Both could be different because of redirects.

        """
        for rtype in ['request', 'response']:
            url = entry[rtype]['url']
            version = extraction_function(url, matchers)
            if version:
                return version

    @staticmethod
    def from_body(entry, matchers, extraction_function):
        body = entry['response']['content']['text']

        version = extraction_function(body, matchers)
        if version:
            return version

    @staticmethod
    def from_header(entry, matchers, extraction_function):
        """ Return version from valid headers.
        It only applies on first request.

        """
        headers = entry['response']['headers']
        version = extract_from_headers(headers, matchers, extraction_function)
        if version:
            return version
