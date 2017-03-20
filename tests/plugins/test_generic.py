import pytest
import dukpy

from detectem.core import Detector
from detectem.plugin import load_plugins, get_plugin_by_name
from detectem.utils import extract_version, extract_name, check_presence
from tests import load_from_yaml, tree


class TestGenericMatches(object):
    FIELDS = ['body', 'url', 'header']

    @pytest.fixture()
    def plugin_list(self):
        return load_plugins()

    def pytest_generate_tests(self, metafunc):
        fname = metafunc.function.__name__

        plugin = pytest.config.getoption('plugin', None)
        if plugin:
            plugin = plugin.replace('.', '')
            data = load_from_yaml(__file__, 'fixtures/{}.yml'.format(plugin))
        else:
            data = load_from_yaml(__file__, 'fixtures/')

        if fname == 'test_matches':
            entry_name = 'matches'
        elif fname == 'test_js_matches':
            entry_name = 'js_matches'
        elif fname == 'test_modular_matches':
            entry_name = 'modular_matches'
        elif fname == 'test_indicators':
            entry_name = 'indicators'

        cases = []
        for entry in data:
            for match in entry.get(entry_name, []):
                cases.append([entry['plugin'], match])

        metafunc.parametrize('plugin_name,match', cases)

    def _get_har_entry_and_method(self, field, match):
        fake_har_entry = tree()

        if field == 'url':
            method = Detector.from_url
            fake_har_entry['request']['url'] = match['url']
        elif field == 'body':
            method = Detector.from_body
            fake_har_entry['response']['content']['text'] = match['body']
        elif field == 'header':
            method = Detector.from_header
            fake_har_entry['response']['headers'] = [match['header']]

        return (fake_har_entry, method)

    def test_matches(self, plugin_name, match, plugin_list):
        field = [k for k in match.keys() if k in self.FIELDS][0]
        fake_har_entry, method = self._get_har_entry_and_method(field, match)

        plugin = get_plugin_by_name(plugin_name, plugin_list)
        matchers = plugin._get_matchers(field)
        results = method(fake_har_entry, matchers, extract_version)

        assert results
        assert match['version'] in results

    def test_js_matches(self, plugin_name, match, plugin_list):
        was_asserted = False
        js_code = match['js']

        interpreter = dukpy.JSInterpreter()
        # Create window browser object
        interpreter.evaljs('window = {};')
        interpreter.evaljs(js_code)

        plugin = get_plugin_by_name(plugin_name, plugin_list)
        for matcher in plugin.js_matchers:
            is_present = interpreter.evaljs(matcher['check'])
            if is_present is not None:
                version = interpreter.evaljs(matcher['version'])
                assert match['version'] == version
                was_asserted = True

        assert was_asserted

    def test_modular_matches(self, plugin_name, match, plugin_list):
        plugin = get_plugin_by_name(plugin_name, plugin_list)
        keys_to_search = [
            ('software', 'modular_matchers', extract_name),
            ('version', 'matchers', extract_version),
        ]

        for kts, source, extraction_fn in keys_to_search:
            flag = False

            for field in match.keys():
                if field not in self.FIELDS:
                    continue

                fake_har_entry, method = self._get_har_entry_and_method(field, match)
                matchers = plugin._get_matchers(field, source)
                results = method(fake_har_entry, matchers, extraction_fn)
                if results and match[kts] in results:
                    flag = True
                    break

            assert flag

    def test_indicators(self, plugin_name, match, plugin_list):
        field = [k for k in match.keys() if k in self.FIELDS][0]
        fake_har_entry, method = self._get_har_entry_and_method(field, match)

        plugin = get_plugin_by_name(plugin_name, plugin_list)
        matchers = plugin._get_matchers(field, 'indicators')
        presence = method(fake_har_entry, matchers, check_presence)

        assert presence
