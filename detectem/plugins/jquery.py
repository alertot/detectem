from detectem.plugin import Plugin


class JqueryPlugin(Plugin):
    name = "jquery"
    homepage = "https://jquery.com/"
    tags = ["javascript", "jquery"]

    matchers = [
        {"body": r"/\*\!? jQuery v(?P<version>[0-9\.]+)( \S+)? \| \(c\)"},
        {"body": r"/\*\!? jQuery v(?P<version>[0-9\.]+) \| \(c\)"},
        {
            "body": r"/\*\!? jQuery v(?P<version>[0-9\.]+) jquery.com \| jquery.org/license"
        },
        {"body": r"\* jQuery JavaScript Library v(?P<version>[0-9\.]+)"},
        {"url": r"/jquery/(?P<version>[0-9\.]+)/jquery(\.slim)?(\.min)?\.js"},
        {"url": r"/jquery-(?P<version>[0-9\.]+)(\.slim)?(\.min)?\.js"},
        {"dom": ('"jQuery" in window', "window.jQuery().jquery")},
    ]


class ColorBoxPlugin(Plugin):
    name = "jquery-colorbox"
    homepage = "http://www.jacklmoore.com/colorbox/"
    tags = ["javascript", "jquery"]

    matchers = [{"body": r"// ColorBox v(?P<version>[0-9\.]+) - a full featured"}]


class JqueryMigratePlugin(Plugin):
    name = "jquery-migrate"
    homepage = "https://github.com/jquery/jquery-migrate"
    tags = ["javascript", "jquery"]

    matchers = [{"body": r"/*! jQuery Migrate v(?P<version>[0-9\.]+) \| \(c\) jQuery"}]
