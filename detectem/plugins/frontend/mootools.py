from detectem.plugin import Plugin


class MooToolsCorePlugin(Plugin):
    name = 'mootools-core'
    homepage = 'https://mootools.net/core'
    js_matchers = [
        {'check': 'window.MooTools', 'version': 'window.MooTools.version'},
    ]


class MooToolsMorePlugin(Plugin):
    name = 'mootools-more'
    homepage = 'https://mootools.net/more'
    js_matchers = [
        {
            'check': 'window.MooTools && window.MooTools.More',
            'version': 'window.MooTools.More.version'
        },
    ]
