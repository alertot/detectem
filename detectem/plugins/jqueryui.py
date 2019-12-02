from detectem.plugin import Plugin


class JqueryUiPlugin(Plugin):
    name = "jqueryui"
    homepage = "http://jqueryui.com"
    tags = ["javascript", "jquery"]

    matchers = [
        {"body": r"jQuery UI (\w+ )+(?P<version>[0-9\.]+)"},
        {"body": r"/\*! jQuery UI - v(?P<version>[0-9\.]+)"},
        {"url": r"ui/(?P<version>[0-9\.]+)/jquery-ui(\.min)?\.js"},
    ]
