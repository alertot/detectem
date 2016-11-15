from detectem.plugin import Plugin


class MomentJSPlugin(Plugin):
    name = 'moment.js'
    matchers = [
        {'url': '/moment\.js/(?P<version>[0-9\.]+)/moment(\.min)?\.js'},
    ]
