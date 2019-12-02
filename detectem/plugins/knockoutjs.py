from detectem.plugin import Plugin


class KnockoutJSPlugin(Plugin):
    name = "knockoutjs"
    homepage = "http://knockoutjs.com/"
    vendor = "Steve Sanderson"
    tags = ["javascript", "knockout", "js framework"]

    matchers = [
        {"body": r"^//\s+Knockout\.js (?P<version>[0-9\.]+)"},
        {"url": r"/knockout(.js)?/(?P<version>[0-9\.]+)/knockout(-min)?\.js"},
        {"url": r"/knockout-(?P<version>[0-9\.]+|latest)(\.min)?\.js"},
        {"dom": ("window.ko", "window.ko.version")},
        {"xpath": ('//script[@data-requiremodule="knockout"]', None)},
    ]
