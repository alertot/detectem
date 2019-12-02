import pytest

from detectem.core import MATCHERS
from detectem.plugin import GenericPlugin, load_plugins
from tests import create_pm

from .utils import create_har_entry


class TestGenericPlugin:
    @pytest.fixture
    def plugins(self):
        return load_plugins()

    def test_generic_plugin(self):
        class MyGenericPlugin(GenericPlugin):
            pass

        x = MyGenericPlugin()
        with pytest.raises(NotImplementedError):
            x.get_information(entry=None)

        assert x.ptype == "generic"

    @pytest.mark.parametrize(
        "plugin_name,matcher_type,har_content,name",
        [
            (
                "wordpress_generic",
                "url",
                "http://domain.tld/wp-content/plugins/example/",
                "example",
            )
        ],
    )
    def test_real_generic_plugin(
        self, plugin_name, matcher_type, har_content, name, plugins
    ):
        plugin = plugins.get(plugin_name)
        har_entry = create_har_entry(matcher_type, value=har_content)

        # Verify presence using matcher class
        matchers = plugin.get_matchers(matcher_type)
        matcher_class = MATCHERS[matcher_type]

        assert matcher_class.get_info(har_entry, *matchers) == create_pm(presence=True)

        assert plugin.get_information(har_entry)["name"] == name
