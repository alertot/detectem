from detectem.plugin import Plugin


class MomentJSPlugin(Plugin):
    name = 'moment.js'
    homepage = 'http://momentjs.com/'
    matchers = [
        {'url': '/moment\.js/(?P<version>[0-9\.]+)/moment(\.min)?\.js'},
    ]
