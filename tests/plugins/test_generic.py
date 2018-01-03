import os

import pytest
import dukpy

from importlib.util import find_spec

from detectem.core import MATCHERS
from detectem.plugin import load_plugins
from detectem.settings import PLUGIN_PACKAGES
from tests import load_from_yaml, tree


class TestGenericMatches(object):
    FIELDS = ['body', 'url', 'header', 'xpath']

    def pytest_generate_tests(self, metafunc):
        fname = metafunc.function.__name__
        cases = []
        all_plugins = load_plugins()

        for plugin_package in PLUGIN_PACKAGES:
            package = plugin_package.split('.')[0]
            package_dir = find_spec(package).submodule_search_locations[0]
            test_dir = os.path.join(package_dir, os.pardir, 'tests')

            plugin = pytest.config.getoption('plugin', None)
            data = load_from_yaml(test_dir, 'plugins/fixtures/')

            if fname == 'test_version_matches':
                entry_name = 'matches'
            elif fname == 'test_js_matches':
                entry_name = 'js_matches'
            elif fname == 'test_modular_matches':
                entry_name = 'modular_matches'
            elif fname == 'test_indicators':
                entry_name = 'indicators'

            for entry in data:
                for yaml_dict in entry.get(entry_name, []):
                    if plugin:
                        if plugin == entry['plugin']:
                            p = all_plugins.get(entry['plugin'])
                            cases.append([p, yaml_dict])
                    else:
                        p = all_plugins.get(entry['plugin'])
                        cases.append([p, yaml_dict])

        metafunc.parametrize('plugin,yaml_dict', cases)

    def _get_har_entry(self, yaml_dict, field):
        fake_har_entry = tree()

        if field == 'url':
            fake_har_entry['request']['url'] = yaml_dict['url']
            fake_har_entry['response']['url'] = yaml_dict['url']
        elif field == 'body':
            fake_har_entry['response']['content']['text'] = yaml_dict['body']
        elif field == 'header':
            fake_har_entry['response']['headers'] = [yaml_dict['header']]
        elif field == 'xpath':
            fake_har_entry['response']['content']['text'] = yaml_dict['xpath']

        return fake_har_entry

    def _get_value_from_method(self, plugin, yaml_dict, method_name):
        sources = {
            'get_version': 'matchers',
            'get_module_name': 'modular_matchers',
            'check_presence': 'indicators',
        }
        field = [k for k in yaml_dict.keys() if k in self.FIELDS][0]
        method = getattr(MATCHERS[field], method_name)
        har_entry = self._get_har_entry(yaml_dict, field)

        matchers = plugin._get_matchers(field, source=sources[method_name])
        return method(har_entry, *matchers)

    def test_version_matches(self, plugin, yaml_dict):
        result = self._get_value_from_method(plugin, yaml_dict, 'get_version')

        assert yaml_dict['version'] == result

    def test_js_matches(self, plugin, yaml_dict):
        was_asserted = False
        js_code = yaml_dict['js']

        interpreter = dukpy.JSInterpreter()
        # Create window browser object
        interpreter.evaljs('window = {};')
        interpreter.evaljs(js_code)

        for matcher in plugin.js_matchers:
            is_present = interpreter.evaljs(matcher['check'])
            if is_present is not None:
                version = interpreter.evaljs(matcher['version'])
                assert yaml_dict['version'] == version
                was_asserted = True

        assert was_asserted

    def test_modular_matches(self, plugin, yaml_dict):
        result = self._get_value_from_method(plugin, yaml_dict, 'get_module_name')

        assert yaml_dict['module_name'] == result

    def test_indicators(self, plugin, yaml_dict):
        result = self._get_value_from_method(plugin, yaml_dict, 'check_presence')

        assert result
