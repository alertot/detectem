import pytest
import dukpy

from detectem.core import Detector
from detectem.plugin import load_plugins, get_plugin_by_name

from tests import load_from_yaml, tree


class TestGenericMatches(object):
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
            cases = []
            for entry in data:
                for match in entry['matches']:
                    cases.append([entry['plugin'], match])

            metafunc.parametrize('plugin_name,match', cases)
        elif fname == 'test_js_matches':
            cases = []
            for entry in data:
                for match in entry.get('js_matches', []):
                    cases.append([entry['plugin'], match])

            metafunc.parametrize('plugin_name,match', cases)


    def test_matches(self, plugin_name, match, plugin_list):
        fake_har_entry = tree()
        if 'url' in match:
            method = Detector.get_version_from_url
            fake_har_entry['request']['url'] = match['url']
        elif 'body' in match:
            method = Detector.get_version_from_body
            fake_har_entry['response']['content']['text'] = match['body']
        elif 'header' in match:
            method = Detector.get_version_from_headers
            fake_har_entry['response']['headers'] = [match['header']]

        plugin = get_plugin_by_name(plugin_name, plugin_list)

        results = method(plugin, fake_har_entry)
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

