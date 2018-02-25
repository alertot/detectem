from detectem.plugin import Plugin


class ReactPlugin(Plugin):
    name = 'react'
    homepage = 'https://facebook.github.io/react/'
    tags = ['javascript', 'react']

    matchers = [
        {'body': r' \* React v(?P<version>[0-9\.]+)'},
        {'url': r'/react/(?P<version>[0-9\.]+)/react(-with-addons)?(\.min)?\.js'},
        {'url': r'/react(-with-addons)?-(?P<version>[0-9\.]+)(\.min)?\.js'},
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
