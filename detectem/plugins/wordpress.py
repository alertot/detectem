from detectem.plugin import Plugin

from .helpers import meta_generator


class WordpressPlugin(Plugin):
    name = "wordpress"
    homepage = "https://wordpress.org/"
    tags = ["wordpress"]

    matchers = [
        {"url": r"/wp-includes/js/wp-embed.min.js\?ver=(?P<version>[0-9\.]+)"},
        {"xpath": (meta_generator("Wordpress"), r"(?P<version>[0-9\.]+)")},
        {"url": "/wp-content/plugins/"},
    ]
