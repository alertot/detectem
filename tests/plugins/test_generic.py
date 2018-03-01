import pytest

from detectem.core import MATCHERS
from detectem.plugin import load_plugins, GenericPlugin
from .utils import create_har_entry


class TestGenericPlugin(object):
    @pytest.fixture
    def plugins(self):
        return load_plugins()

    def test_generic_plugin(self):
        class MyGenericPlugin(GenericPlugin):
            pass

        x = MyGenericPlugin()
        with pytest.raises(NotImplementedError):
            x.get_information(entry=None)

        assert x.ptype == 'generic'

    @pytest.mark.parametrize('plugin_name,indicator,name', [
        (
            'wordpress_generic',
            {'url': 'http://domain.tld/wp-content/plugins/example/'},
            'example',
        )
    ])
    def test_real_generic_plugin(self, plugin_name, indicator, name, plugins):
        plugin = plugins.get(plugin_name)
        matcher_type = [k for k in indicator.keys()][0]

        har_entry = create_har_entry(indicator, matcher_type)
        matchers_in_plugin = plugin._get_matchers(matcher_type, 'indicators')

        # Call presence method in related matcher class
        matcher_instance = MATCHERS[matcher_type]
        assert matcher_instance.check_presence(har_entry, *matchers_in_plugin)

        assert plugin.get_information(har_entry)['name'] == name
