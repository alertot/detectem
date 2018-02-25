from detectem.plugin import Plugin


class D3JSPlugin(Plugin):
    name = 'd3.js'
    homepage = 'https://d3js.org'
    tags = ['javascript', 'graphics', 'visualization']

    matchers = [
        {'body': r'// https://d3js.org Version (?P<version>[0-9\.]+)\. Copyright'},
        {'url': r'[dD]3(\.js)?/(?P<version>[0-9\.]+)/d3(\.min)?\.js'},
    ]
    js_matchers = [
        {'check': 'window.d3', 'version': 'window.d3.version'},
    ]
