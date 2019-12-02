import json
import pkgutil
import re

from detectem.plugin import GenericPlugin
from detectem.utils import get_url


class WordpressGenericPlugin(GenericPlugin):
    name = "wordpress_generic"
    homepage = "https://wordpress.org/plugins/%s/"
    tags = ["wordpress"]
    plugins = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        wordpress_data = pkgutil.get_data("detectem", "data/wordpress.jl")
        for line in wordpress_data.splitlines():
            data = json.loads(line)
            self.plugins[data["name"]] = data["vendor"]

    matchers = [{"url": "/wp-content/plugins/"}]

    def get_information(self, entry):
        name_match = re.findall("/wp-content/plugins/([^/]+)/", get_url(entry))
        # There are weird cases with malformed plugins urls
        if not name_match:
            return {}

        name = name_match[0].lower()
        homepage = self.homepage % name

        try:
            vendor = self.plugins[name]
        except KeyError:
            vendor = None

        return {"name": name, "homepage": homepage, "vendor": vendor}
