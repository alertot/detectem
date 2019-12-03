from detectem.plugin import Plugin


class MomentJSPlugin(Plugin):
    name = "moment.js"
    homepage = "http://momentjs.com/"
    tags = ["javascript"]

    matchers = [
        {"body": r"//! moment\.js\s+//! version : (?P<version>[0-9\.]+)"},
        {"url": r"/moment\.js/(?P<version>[0-9\.]+)/moment(\.min)?\.js"},
        {"dom": ("window.moment", "window.moment.version")},
    ]
