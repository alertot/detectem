from detectem.plugin import Plugin


class BackboneJsPlugin(Plugin):
    name = "backbone.js"
    homepage = "http://backbonejs.org"
    tags = ["backbone", "js framework"]

    matchers = [
        {"body": r"^//\s+Backbone\.js (?P<version>[0-9\.]+)"},
        {"url": r"/backbone\.?js/(?P<version>[0-9\.]+)/backbone(-min)?\.js"},
        {"url": r"/backbone-(?P<version>[0-9\.]+)(\.min)?\.js"},
        {"dom": ("window.Backbone", "window.Backbone.VERSION")},
    ]
    hints = ["underscore.js"]
