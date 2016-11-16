from detectem.plugin import Plugin


class IISPlugin(Plugin):
    name = 'iis'
    homepage = 'https://www.iis.net/'
    matchers = [
        {'header': ('Server', 'Microsoft-IIS/(?P<version>[0-9\.]+)')},
    ]
