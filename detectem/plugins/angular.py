from detectem.plugin import Plugin


class AngularPlugin(Plugin):
    name = "angular"
    homepage = "https://angular.io/"
    tags = ["angular", "js framework"]
    matchers = [
        {"body": r"<[^>]+ ng-version=\"(?P<version>[0-9a-z\.-]+)\""},
        {
            "dom": (
                "window.getAllAngularRootElements",
                'window.getAllAngularRootElements()[0].attributes["ng-version"].value',
            )
        },
        {"dom": ("window.ng && window.ng.coreTokens", None)},
    ]
