from detectem.plugin import Plugin
from detectem.plugins.helpers import meta_generator


class GhostPlugin(Plugin):
    name = "ghost"
    homepage = "https://www.ghost.org/"
    tags = ["blog", "node.js"]

    matchers = [{"xpath": (meta_generator("Ghost"), r"(?P<version>[0-9\.]+)")}]
