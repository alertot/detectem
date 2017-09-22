from detectem.plugin import Plugin


class BackboneJsPlugin(Plugin):
    name = 'backbone.js'
    homepage = 'http://backbonejs.org'
    matchers = [
        {'body': '^//\s+Backbone\.js (?P<version>[0-9\.]+)'},
        {'url': '/backbone\.?js/(?P<version>[0-9\.]+)/backbone(-min)?\.js'},
        {'url': '/backbone-(?P<version>[0-9\.]+)(\.min)?\.js'},
    ]
    js_matchers = [
        {
            'check': 'window.Backbone',
            'version': 'window.Backbone.VERSION'
        },
    ]
    hints = ['underscore.js']
