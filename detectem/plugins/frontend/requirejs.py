from detectem.plugin import Plugin


class RequireJSPlugin(Plugin):
    name = 'require.js'
    homepage = 'http://requirejs.org/'
    matchers = [
        {'body': '\* @license RequireJS (?P<version>[0-9\.]+)'},
        {'url': '/require\.js/(?P<version>[0-9\.]+)/require(\.min)?\.js'},
    ]
