from detectem.plugin import Plugin


class ReactPlugin(Plugin):
    name = "react"
    homepage = "https://facebook.github.io/react/"
    tags = ["javascript", "react"]
    vendor = "Facebook"

    matchers = [
        {"body": r" \* React v(?P<version>[0-9\.]+)"},
        {"url": r"/react/(?P<version>[0-9\.]+)/react(-with-addons)?(\.min)?\.js"},
        {"url": r"/react(-with-addons)?-(?P<version>[0-9\.]+)(\.min)?\.js"},
        {"dom": ("window.React", "window.React.version")},
        {"xpath": ("//div[@data-reactid]", None)},
    ]
