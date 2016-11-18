from detectem.plugin import Plugin


class JqueryPlugin(Plugin):
    name = 'jquery'
    homepage = 'https://jquery.com/'
    matchers = [
        {'body': '/\*\!? jQuery v(?P<version>[0-9\.]+) \| \(c\)'},
        {'body': '\* jQuery JavaScript Library v(?P<version>[0-9\.]+)'},
        {'url': '/jquery/(?P<version>[0-9\.]+)/jquery(\.min)?\.js'},
        {'url': '/jquery-(?P<version>[0-9\.]+)(\.min)?\.js'},
    ]


class ColorBoxPlugin(Plugin):
    name = 'jquery_colorbox'
    homepage = 'http://www.jacklmoore.com/colorbox/'
    matchers = [
        {'body': '// ColorBox v(?P<version>[0-9\.]+) - a full featured'}
    ]
