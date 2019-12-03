import logging
import urllib.parse

from detectem.matchers import BodyMatcher, HeaderMatcher, UrlMatcher, XPathMatcher
from detectem.results import Result, ResultCollection
from detectem.settings import (
    GENERIC_TYPE,
    HINT_TYPE,
    INDICATOR_TYPE,
    INLINE_SCRIPT_ENTRY,
    MAIN_ENTRY,
    RESOURCE_ENTRY,
)
from detectem.utils import get_most_complete_pm, get_url, get_version_via_file_hashes

logger = logging.getLogger("detectem")
MATCHERS = {
    "url": UrlMatcher(),
    "body": BodyMatcher(),
    "header": HeaderMatcher(),
    "xpath": XPathMatcher(),
}


class HarProcessor:
    """ This class process the HAR list returned by Splash
        adding some useful markers for matcher application
    """

    @staticmethod
    def _set_entry_type(entry, entry_type):
        """ Set entry type (detectem internal metadata) """
        entry.setdefault("detectem", {})["type"] = entry_type

    @staticmethod
    def _get_location(entry):
        """ Return `Location` header value if it's present in ``entry`` """
        headers = entry["response"].get("headers", [])

        for header in headers:
            if header["name"] == "Location":
                return header["value"]

        return None

    @classmethod
    def _script_to_har_entry(cls, script, url):
        """ Return entry for embed script """
        entry = {
            "request": {"url": url},
            "response": {"url": url, "content": {"text": script}},
        }

        cls._set_entry_type(entry, INLINE_SCRIPT_ENTRY)

        return entry

    def mark_entries(self, entries):
        """ Mark one entry as main entry and the rest as resource entry.

            Main entry is the entry that contain response's body
            of the requested URL.
        """

        for entry in entries:
            self._set_entry_type(entry, RESOURCE_ENTRY)

        # If first entry doesn't have a redirect, set is as main entry
        main_entry = entries[0]
        main_location = self._get_location(main_entry)
        if not main_location:
            self._set_entry_type(main_entry, MAIN_ENTRY)
            return

        # Resolve redirected URL and see if it's in the rest of entries
        main_url = urllib.parse.urljoin(get_url(main_entry), main_location)
        for entry in entries[1:]:
            url = get_url(entry)
            if url == main_url:
                self._set_entry_type(entry, MAIN_ENTRY)
                break
        else:
            # In fail case, set the first entry
            self._set_entry_type(main_entry, MAIN_ENTRY)

    def prepare(self, response, url):
        har = response.get("har", [])
        if har:
            self.mark_entries(har)

        # Detect embed scripts and add them to HAR list
        for script in response.get("scripts", []):
            har.append(self._script_to_har_entry(script, url))

        return har


class Detector:
    def __init__(self, response, plugins, requested_url):
        self.requested_url = requested_url
        self.har = HarProcessor().prepare(response, requested_url)

        self._softwares_from_splash = response["softwares"]
        self._plugins = plugins
        self._results = ResultCollection()

    @staticmethod
    def _get_entry_type(entry):
        """ Return entry type. """
        return entry["detectem"]["type"]

    def get_hints(self, plugin):
        """ Return plugin hints from ``plugin``. """
        hints = []

        for hint_name in getattr(plugin, "hints", []):
            hint_plugin = self._plugins.get(hint_name)
            if hint_plugin:
                hint_result = Result(
                    name=hint_plugin.name,
                    homepage=hint_plugin.homepage,
                    from_url=self.requested_url,
                    type=HINT_TYPE,
                    plugin=plugin.name,
                )
                hints.append(hint_result)

                logger.debug(f"{plugin.name} & hint {hint_result.name} detected")
            else:
                logger.error(f"{plugin.name} hints an invalid plugin: {hint_name}")

        return hints

    def process_from_splash(self):
        """ Add softwares found in the DOM """
        for software in self._softwares_from_splash:
            plugin = self._plugins.get(software["name"])

            # Determine if it's a version or presence result
            try:
                additional_data = {"version": software["version"]}
            except KeyError:
                additional_data = {"type": INDICATOR_TYPE}

            self._results.add_result(
                Result(
                    name=plugin.name,
                    homepage=plugin.homepage,
                    from_url=self.requested_url,
                    plugin=plugin.name,
                    **additional_data,
                )
            )

            for hint in self.get_hints(plugin):
                self._results.add_result(hint)

    def _get_matchers_for_entry(self, plugin, entry):
        grouped_matchers = plugin.get_grouped_matchers()

        def remove_group(group):
            if group in grouped_matchers:
                del grouped_matchers[group]

        if self._get_entry_type(entry) == MAIN_ENTRY:
            remove_group("body")
            remove_group("url")
        else:
            remove_group("header")
            remove_group("xpath")

        remove_group("dom")

        return grouped_matchers

    def apply_plugin_matchers(self, plugin, entry):
        data_list = []
        grouped_matchers = self._get_matchers_for_entry(plugin, entry)

        for matcher_type, matchers in grouped_matchers.items():
            klass = MATCHERS[matcher_type]
            plugin_match = klass.get_info(entry, *matchers)
            if plugin_match.name or plugin_match.version or plugin_match.presence:
                data_list.append(plugin_match)

        return get_most_complete_pm(data_list)

    def process_har(self):
        """ Detect plugins present in the page. """
        hints = []

        version_plugins = self._plugins.with_version_matchers()
        generic_plugins = self._plugins.with_generic_matchers()

        for entry in self.har:
            for plugin in version_plugins:
                pm = self.apply_plugin_matchers(plugin, entry)
                if not pm:
                    continue

                # Set name if matchers could detect modular name
                if pm.name:
                    name = "{}-{}".format(plugin.name, pm.name)
                else:
                    name = plugin.name

                if pm.version:
                    self._results.add_result(
                        Result(
                            name=name,
                            version=pm.version,
                            homepage=plugin.homepage,
                            from_url=get_url(entry),
                            plugin=plugin.name,
                        )
                    )
                elif pm.presence:
                    # Try to get version through file hashes
                    version = get_version_via_file_hashes(plugin, entry)
                    if version:
                        self._results.add_result(
                            Result(
                                name=name,
                                version=version,
                                homepage=plugin.homepage,
                                from_url=get_url(entry),
                                plugin=plugin.name,
                            )
                        )
                    else:
                        self._results.add_result(
                            Result(
                                name=name,
                                homepage=plugin.homepage,
                                from_url=get_url(entry),
                                type=INDICATOR_TYPE,
                                plugin=plugin.name,
                            )
                        )
                hints += self.get_hints(plugin)

            for plugin in generic_plugins:
                pm = self.apply_plugin_matchers(plugin, entry)
                if not pm:
                    continue

                plugin_data = plugin.get_information(entry)

                # Only add to results if it's a valid result
                if "name" in plugin_data:
                    self._results.add_result(
                        Result(
                            name=plugin_data["name"],
                            homepage=plugin_data["homepage"],
                            from_url=get_url(entry),
                            type=GENERIC_TYPE,
                            plugin=plugin.name,
                        )
                    )

                hints += self.get_hints(plugin)

        for hint in hints:
            self._results.add_result(hint)

    def get_results(self, metadata=False):
        """ Return results of the analysis. """
        results_data = []

        self.process_har()
        self.process_from_splash()

        for rt in sorted(self._results.get_results()):
            rdict = {"name": rt.name}
            if rt.version:
                rdict["version"] = rt.version

            if metadata:
                rdict["homepage"] = rt.homepage
                rdict["type"] = rt.type
                rdict["from_url"] = rt.from_url
                rdict["plugin"] = rt.plugin

            results_data.append(rdict)

        return results_data
