from detectem.plugin import Plugin


class RequireJSPlugin(Plugin):
    name = "require.js"
    homepage = "http://requirejs.org/"
    tags = ["javascript"]

    matchers = [
        {"body": r"\* @license RequireJS (?P<version>[0-9\.]+)"},
        {"url": r"/require\.js/(?P<version>[0-9\.]+)/require(\.min)?\.js"},
    ]
