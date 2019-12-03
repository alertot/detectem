from detectem.plugin import Plugin


class UnderscoreJSPlugin(Plugin):
    name = "underscore.js"
    homepage = "http://underscorejs.org/"
    vendor = "Jeremy Ashkenas"
    tags = ["javascript"]

    matchers = [
        {"body": r"^//\s+Underscore\.js (?P<version>[0-9\.]+)"},
        {"url": r"/underscore\.?js/(?P<version>[0-9\.]+)/underscore(-min)?\.js"},
        {"url": r"/underscore-(?P<version>[0-9\.]+)(\.min)?\.js"},
    ]
