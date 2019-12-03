import os

from importlib.util import find_spec

import dukpy
import pytest

from detectem.core import MATCHERS
from detectem.plugin import load_plugins
from detectem.settings import PLUGIN_PACKAGES
from tests import create_pm, load_from_yaml

from .utils import create_har_entry


class TestCommonMatches:
    FIELDS = [k for k in MATCHERS]

    def pytest_generate_tests(self, metafunc):
        fname = metafunc.function.__name__
        cases = []
        all_plugins = load_plugins()

        for plugin_package in PLUGIN_PACKAGES:
            package = plugin_package.split(".")[0]
            package_dir = find_spec(package).submodule_search_locations[0]
            test_dir = os.path.join(package_dir, os.pardir, "tests")

            plugin = metafunc.config.getoption("plugin", None)
            data = load_from_yaml(test_dir, "plugins/fixtures/")

            only_dom_matches = fname == "test_dom_matches"

            # Entry is the full plugin test file evaluated as a dictionary
            for entry in data:
                # Each yaml_dict is an entry in matches
                for yaml_dict in entry["matches"]:
                    # Filter valid matchers if dom matchers are expected
                    if (only_dom_matches and "dom" not in yaml_dict) or (
                        not only_dom_matches and "dom" in yaml_dict
                    ):
                        continue

                    if plugin:
                        # Case if plugin was provided by developer
                        if plugin == entry["plugin"]:
                            p = all_plugins.get(entry["plugin"])
                            cases.append([p, yaml_dict])
                    else:
                        p = all_plugins.get(entry["plugin"])
                        cases.append([p, yaml_dict])

        metafunc.parametrize("plugin,yaml_dict", cases)

    def _get_plugin_match(self, plugin, yaml_dict):
        field = [k for k in yaml_dict.keys() if k in self.FIELDS][0]
        har_entry = create_har_entry(field, yaml_dict)

        matchers = plugin.get_matchers(field)
        matcher_class = MATCHERS[field]

        return matcher_class.get_info(har_entry, *matchers)

    def test_matches(self, plugin, yaml_dict):
        pm = self._get_plugin_match(plugin, yaml_dict)

        # More than one value could be asserted, then we need to create this dict
        asserter = {
            k: v for k, v in yaml_dict.items() if k in ["version", "name", "presence"]
        }
        assert pm == create_pm(**asserter)

    def test_dom_matches(self, plugin, yaml_dict):
        was_asserted = False  # At least one assert was done
        js_code = yaml_dict["dom"]

        interpreter = dukpy.JSInterpreter()
        # Create window browser object
        interpreter.evaljs("window = {};")
        interpreter.evaljs(js_code)

        for matcher in plugin.get_matchers("dom"):
            check_statement, version_statement = matcher

            is_present = interpreter.evaljs(check_statement)
            if is_present is not None:
                if version_statement:
                    version = interpreter.evaljs(version_statement)
                    assert yaml_dict["version"] == version

                    was_asserted = True
                    break
                else:
                    assert yaml_dict["presence"]
                    was_asserted = True

        assert was_asserted
