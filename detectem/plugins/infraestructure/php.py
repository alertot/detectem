from detectem.plugin import Plugin


class PhpPlugin(Plugin):
    name = 'php'
    homepage = 'http://php.net/'
    matchers = [
        {'header': ('X-Powered-By', 'PHP/(?P<version>[0-9\.]+)')},
    ]
