from detectem.plugin import Plugin


class MomentJSPlugin(Plugin):
    name = 'moment.js'
    homepage = 'http://momentjs.com/'
    matchers = [
        {'body': '//! moment\.js\s+//! version : (?P<version>[0-9\.]+)'},
        {'url': '/moment\.js/(?P<version>[0-9\.]+)/moment(\.min)?\.js'},
    ]
    js_matchers = [
        {
            'check': 'window.moment',
            'version': 'window.moment.version'
        },
    ]
