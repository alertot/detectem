from detectem.plugin import Plugin


class NginxPlugin(Plugin):
    name = 'nginx'
    matchers = [
        {'header': ('Server', 'nginx/(?P<version>[0-9\.]+)')},
    ]
