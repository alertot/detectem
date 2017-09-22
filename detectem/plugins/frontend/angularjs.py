from detectem.plugin import Plugin


class AngularjsPlugin(Plugin):
    name = 'angularjs'
    homepage = 'https://angularjs.org/'
    matchers = [
        {'body': '^/\*\s+AngularJS v(?P<version>[0-9a-z\.-]+)\s'},
        {'url': 'angular\.?js/(?P<version>[0-9\.]+)/angular(\.min)?\.js'},
    ]
    modular_matchers = [
        {'url': '/(?:angular-)(?P<name>\w+)(\.min)?\.js'},
    ]
    js_matchers = [
        {
            'check': 'window.angular && window.angular.version',
            'version': 'window.angular.version.full'
        },
    ]
