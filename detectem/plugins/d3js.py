from detectem.plugin import Plugin


class D3JSPlugin(Plugin):
    name = "d3.js"
    homepage = "https://d3js.org"
    vendor = "Mike Bostock"
    tags = ["javascript", "graphics", "visualization"]

    matchers = [
        {"body": r"// https://d3js.org Version (?P<version>[0-9\.]+)\. Copyright"},
        {"url": r"[dD]3(\.js)?/(?P<version>[0-9\.]+)/d3(\.min)?\.js"},
        {"dom": ("window.d3", "window.d3.version")},
    ]
