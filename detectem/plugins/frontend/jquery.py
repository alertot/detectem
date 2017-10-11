from detectem.plugin import Plugin


class JqueryPlugin(Plugin):
    name = 'jquery'
    homepage = 'https://jquery.com/'
    matchers = [
        {'body': '/\*\!? jQuery v(?P<version>[0-9\.]+)( \S+)? \| \(c\)'},
        {'body': '/\*\!? jQuery v(?P<version>[0-9\.]+) \| \(c\)'},
        {'body': '/\*\!? jQuery v(?P<version>[0-9\.]+) jquery.com \| jquery.org/license'},
        {'body': '\* jQuery JavaScript Library v(?P<version>[0-9\.]+)'},
        {'url': '/jquery/(?P<version>[0-9\.]+)/jquery(\.slim)?(\.min)?\.js'},
        {'url': '/jquery-(?P<version>[0-9\.]+)(\.slim)?(\.min)?\.js'},
    ]
    js_matchers = [
        {'check': '"jQuery" in window', 'version': 'window.jQuery().jquery'},
    ]


class ColorBoxPlugin(Plugin):
    name = 'jquery-colorbox'
    homepage = 'http://www.jacklmoore.com/colorbox/'
    matchers = [
        {'body': '// ColorBox v(?P<version>[0-9\.]+) - a full featured'}
    ]


class JqueryMigratePlugin(Plugin):
    name = 'jquery-migrate'
    homepage = 'https://github.com/jquery/jquery-migrate'
    matchers = [
        {'body': '/*! jQuery Migrate v(?P<version>[0-9\.]+) \| \(c\) jQuery'},
    ]
