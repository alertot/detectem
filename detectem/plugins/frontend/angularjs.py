from detectem.plugin import Plugin


class AngularjsPlugin(Plugin):
    name = 'angularjs'
    homepage = 'https://angularjs.org/'
    matchers = [
        {'body': '^/\*\s+AngularJS v(?P<version>.+?)\s'},
    ]
    modular_matchers = [
        {'url': '/(?:angular-)(?P<name>\w+)\.min\.js'},
    ]
