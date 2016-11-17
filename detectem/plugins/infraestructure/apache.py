from detectem.plugin import Plugin


class ApachePlugin(Plugin):
    name = 'apache'
    homepage = 'http://httpd.apache.org/'
    matchers = [
        {'header': ('Server', 'Apache/(?P<version>[0-9\.]+)')},
    ]


class ApacheCoyotePlugin(Plugin):
    name = 'apache_coyote'
    homepage = 'http://httpd.apache.org/'
    matchers = [
        {'header': ('Server', 'Apache-Coyote/(?P<version>[0-9\.]+)')},
    ]
