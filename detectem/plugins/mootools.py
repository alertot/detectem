from detectem.plugin import Plugin


class MooToolsCorePlugin(Plugin):
    name = "mootools-core"
    homepage = "https://mootools.net/core"
    tags = ["javascript", "mootools"]

    matchers = [{"dom": ("window.MooTools", "window.MooTools.version")}]


class MooToolsMorePlugin(Plugin):
    name = "mootools-more"
    homepage = "https://mootools.net/more"
    tags = ["javascript", "mootools"]

    matchers = [
        {
            "dom": (
                "window.MooTools && window.MooTools.More",
                "window.MooTools.More.version",
            )
        }
    ]
