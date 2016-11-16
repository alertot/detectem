from detectem.plugin import Plugin


class PhpPlugin(Plugin):
    name = 'php'
    matchers = [
        {'header': ('X-Powered-By', 'PHP/(?P<version>[0-9\.]+)')},
    ]
