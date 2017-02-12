import logging
import json
import collections

from detectem.utils import extract_version, extract_version_from_headers
from detectem.plugin import get_plugin_by_name

logger = logging.getLogger('detectem')

Result = collections.namedtuple('Result', 'plugin version')


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
                    t = Result(plugin, version)
                    if t not in self.results:
                        self.results.append(t)

        for software in self.softwares:
            plugin = get_plugin_by_name(software['name'], self.plugins)
            self.results.append(Result(plugin, software['version']))

    def get_results(self, format=None, metadata=False):
        results_data = []

        for rt in self.results:
            rdict = {'name': rt.plugin.name, 'version': rt.version}
            if metadata:
                rdict['homepage'] = rt.plugin.homepage

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

    def detect_plugin_version(self, plugin, entry):
        """ Return a list of (name, version) after applying every plugin matcher. """
        versions = []  # avoid duplicates

        methods = [
            self.get_version_from_url,
            self.get_version_from_body,
        ]

        for method in methods:
            version = method(plugin, entry)
            if version:
                versions.append(version)

        # Run this method just for the first request
        if self._is_first_request(entry):
            version = self.get_version_from_headers(plugin, entry)
            if version:
                versions.append(version)

        return self.get_most_complete_version(versions)

    @staticmethod
    def get_version_from_url(plugin, entry):
        """ Return version from request or response url.
        Both could be different because of redirects.

        """
        matchers = plugin.get_url_matchers()
        if not matchers:
            return

        for rtype in ['request', 'response']:
            url = entry[rtype]['url']
            version = extract_version(url, matchers)
            if version:
                return version

    @staticmethod
    def get_version_from_body(plugin, entry):
        matchers = plugin.get_body_matchers()
        if not matchers:
            return

        body = entry['response']['content']['text']

        version = extract_version(body, matchers)
        if version:
            return version

    @staticmethod
    def get_version_from_headers(plugin, entry):
        """ Return version from valid headers.
        It only applies on first request.

        """
        matchers = plugin.get_header_matchers()
        if not matchers:
            return

        headers = entry['response']['headers']
        version = extract_version_from_headers(headers, matchers)
        if version:
            return version
