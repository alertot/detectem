from detectem.plugin import Plugin


class IISPlugin(Plugin):
    name = 'iis'
    matchers = [
        {'header': ('Server', 'Microsoft-IIS/(?P<version>[0-9\.]+)')},
    ]
