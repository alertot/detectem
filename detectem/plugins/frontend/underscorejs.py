from detectem.plugin import Plugin


class UnderscoreJSPlugin(Plugin):
    name = 'underscore.js'
    homepage = 'http://underscorejs.org/'
    matchers = [
        {'body': '^//\s+Underscore\.js (?P<version>[0-9\.]+)'},
        {'url': '/underscore\.?js/(?P<version>[0-9\.]+)/underscore(-min)?\.js'},
        {'url': '/underscore-(?P<version>[0-9\.]+)(\.min)?\.js'},
    ]
