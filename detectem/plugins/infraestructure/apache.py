from detectem.plugin import Plugin


class ApachePlugin(Plugin):
    name = 'apache'
    matchers = [
        {'header': ('Server', 'Apache/(?P<version>[0-9\.]+)')},
    ]
