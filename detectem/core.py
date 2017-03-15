import logging
import json
import collections

from detectem.utils import (
    extract_version, extract_name, extract_version_from_headers
)
from detectem.plugin import get_plugin_by_name

logger = logging.getLogger('detectem')

Result = collections.namedtuple('Result', 'name version homepage')


class Detector():
    def __init__(self, response, plugins, requested_url):
        self.har = response['har']
        self.softwares = response['softwares']
        self.plugins = plugins
        self.results = []
        self.requested_url = requested_url

    def start_detection(self):
        for entry in self.har:
            for plugin in self.plugins:
                version = self.detect_plugin_version(plugin, entry)
                if version:
                    name = self.detect_plugin_name(plugin, entry)
                    t = Result(name, version, plugin.homepage)
                    if t not in self.results:
                        self.results.append(t)

        # Feedback from Javascript
        for software in self.softwares:
            plugin = get_plugin_by_name(software['name'], self.plugins)
            self.results.append(
                Result(plugin.name, software['version'], plugin.homepage)
            )

    def get_results(self, format=None, metadata=False):
        results_data = []

        for rt in self.results:
            rdict = {'name': rt.name, 'version': rt.version}
            if metadata:
                rdict['homepage'] = rt.homepage

            results_data.append(rdict)

        if format == 'json':
            return json.dumps(results_data)
        else:
            return results_data

    @staticmethod
    def get_most_complete_version(versions):
        """ Return the most complete version.

        i.e. `versions=['1.4', '1.4.4']` it returns '1.4.4' since it's more complete.
        """
        if not versions:
            return

        return max(versions)

    def _is_first_request(self, entry):
        return entry['request']['url'].rstrip('/') == self.requested_url.rstrip('/')

    def get_values_from_matchers(self, entry, matchers, extraction_function):
        values = []

        for key, matchers in matchers.items():
            method = getattr(self, 'from_{}'.format(key))
            value = method(entry, matchers, extraction_function)
            if value:
                values.append(value)

        return values

    def detect_plugin_version(self, plugin, entry):
        """ Return a list of (name, version) after applying every plugin matcher. """
        versions = []
        grouped_matchers = plugin.get_grouped_matchers()

        # Check headers just for the first request
        if not self._is_first_request(entry) and 'headers' in grouped_matchers:
            del grouped_matchers['headers']

        versions = self.get_values_from_matchers(
            entry, grouped_matchers, extract_version
        )
        return self.get_most_complete_version(versions)

    def detect_plugin_name(self, plugin, entry):
        if not plugin.is_modular:
            return plugin.name

        grouped_matchers = plugin.get_grouped_matchers('modular_matchers')
        module_name = self.get_values_from_matchers(
            entry, grouped_matchers, extract_name
        )

        if module_name:
            name = '{}-{}'.format(plugin.name, module_name[0])
        else:
            name = plugin.name

        return name

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
    def from_headers(entry, matchers, _):
        """ Return version from valid headers.
        It only applies on first request.

        """
        headers = entry['response']['headers']
        version = extract_version_from_headers(headers, matchers)
        if version:
            return version
