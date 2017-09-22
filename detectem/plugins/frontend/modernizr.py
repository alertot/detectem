from detectem.plugin import Plugin


class ModernizrPlugin(Plugin):
    name = 'modernizr'
    homepage = 'http://www.modernizr.com/'
    matchers = [
        {'body': '/\* Modernizr (?P<version>[0-9\.]+) \(Custom Build\)'},
        {'url': '/modernizr/(?P<version>[0-9\.]+)/modernizr(\.min)?\.js'},
        {'url': '/modernizr-(?P<version>[0-9\.]+)(\.min)?\.js'},
    ]
    js_matchers = [
        {
            'check': 'window.Modernizr',
            'version': 'window.Modernizr._version'
        },
    ]
