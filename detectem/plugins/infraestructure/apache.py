from detectem.plugin import Plugin


class ApachePlugin(Plugin):
    name = 'apache'
    homepage = 'http://httpd.apache.org/'
    matchers = [
        {'header': ('Server', 'Apache/(?P<version>[0-9\.]+)')},
    ]
