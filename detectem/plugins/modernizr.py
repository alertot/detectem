from detectem.plugin import Plugin


class ModernizrPlugin(Plugin):
    name = "modernizr"
    homepage = "http://www.modernizr.com/"
    tags = ["javascript"]

    matchers = [
        {"body": r"/\* Modernizr (?P<version>[0-9\.]+) \(Custom Build\)"},
        {"url": r"/modernizr/(?P<version>[0-9\.]+)/modernizr(\.min)?\.js"},
        {"url": r"/modernizr-(?P<version>[0-9\.]+)(\.min)?\.js"},
        {"dom": ("window.Modernizr", "window.Modernizr._version")},
    ]
