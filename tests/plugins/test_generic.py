import pytest

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
            data = load_from_yaml(__file__, 'fixtures/{}.yml'.format(plugin))
        else:
            data = load_from_yaml(__file__, 'fixtures/')

        if fname == 'test_matches':
            cases = []
            for entry in data:
                for match in entry['matches']:
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
