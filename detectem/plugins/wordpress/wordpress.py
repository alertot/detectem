from detectem.plugin import Plugin


class WordpressPlugin(Plugin):
    name = 'wordpress'
    homepage = 'https://wordpress.org/'
    matchers = [
        {'url': '/wp-includes/js/wp-embed.min.js\?ver=(?P<version>[0-9\.]+)'},
    ]
