from detectem.plugin import Plugin


class D3JSPlugin(Plugin):
    name = 'd3.js'
    homepage = 'https://d3js.org'
    matchers = [
        {'body': '// https://d3js.org Version (?P<version>[0-9\.]+)\. Copyright'},
    ]

    js_matchers = [
        {'check': 'window.d3', 'version': 'window.d3.version'},
    ]
