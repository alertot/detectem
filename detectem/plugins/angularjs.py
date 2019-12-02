from detectem.plugin import Plugin


class AngularjsPlugin(Plugin):
    name = "angularjs"
    homepage = "https://angularjs.org/"
    tags = ["angular", "js framework"]

    matchers = [
        {"body": r"^/\*\s+AngularJS v(?P<version>[0-9a-z\.-]+)\s"},
        {"url": r"angular\.?js/(?P<version>[0-9\.]+)/angular(\.min)?\.js"},
        {"url": r"/(?:angular-)(?P<name>\w+)(\.min)?\.js"},
        {
            "dom": (
                "window.angular && window.angular.version",
                "window.angular.version.full",
            )
        },
    ]
