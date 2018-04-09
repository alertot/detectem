import re
import os
import json

from detectem.plugin import GenericPlugin
from detectem.settings import DATA_DIR
from detectem.utils import get_url


class WordpressGenericPlugin(GenericPlugin):
    name = 'wordpress_generic'
    homepage = 'https://wordpress.org/plugins/%s/'
    tags = ['wordpress']
    plugins = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open(os.path.join(DATA_DIR, 'wordpress.jl')) as f:
            for line in f:
                data = json.loads(line)
                self.plugins[data['name']] = data['vendor']

    indicators = [{'url': '/wp-content/plugins/'}]

    def get_information(self, entry):
        name = re.findall('/wp-content/plugins/([^/]+)/', get_url(entry))[0]
        known = None

        try:
            vendor = self.plugins[name]
            known = True
        except KeyError:
            vendor = None
            known = False

        homepage = self.homepage % name

        return {
            'name': name,
            'homepage': homepage,
            'vendor': vendor,
            'known': known,
        }
