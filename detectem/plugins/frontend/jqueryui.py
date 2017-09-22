from detectem.plugin import Plugin


class JqueryUiPlugin(Plugin):
    name = 'jqueryui'
    homepage = 'http://jqueryui.com'
    matchers = [
        {'body': 'jQuery UI (\w+ )+(?P<version>[0-9\.]+)'},
        {'body': '/\*! jQuery UI - v(?P<version>[0-9\.]+)'},
        {'url': 'ui/(?P<version>[0-9\.]+)/jquery-ui(\.min)?\.js'},
    ]
