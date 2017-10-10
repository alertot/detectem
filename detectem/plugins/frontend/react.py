from detectem.plugin import Plugin


class ReactPlugin(Plugin):
    name = 'react'
    homepage = 'https://facebook.github.io/react/'
    matchers = [
        {'body': ' \* React v(?P<version>[0-9\.]+)'},
        {'url': '/react/(?P<version>[0-9\.]+)/react(-with-addons)?(\.min)?\.js'},
        {'url': '/react(-with-addons)?-(?P<version>[0-9\.]+)(\.min)?\.js'},
    ]
    js_matchers = [
        {
            'check': 'window.React',
            'version': 'window.React.version'
        },
    ]
    indicators = [
        {'xpath': '//div[@data-reactid]'},
    ]
