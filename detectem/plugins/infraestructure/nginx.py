from detectem.plugin import Plugin


class NginxPlugin(Plugin):
    name = 'nginx'
    homepage = 'https://www.nginx.com/'
    matchers = [
        {'header': ('Server', 'nginx/(?P<version>[0-9\.]+)')},
    ]
