from detectem.plugin import Plugin


class ApachePlugin(Plugin):
    name = 'apache'
    homepage = 'http://httpd.apache.org/'
    matchers = [
        {'header': ('Server', 'Apache/(?P<version>[0-9\.]+)')},
    ]


class ApacheCoyotePlugin(Plugin):
    name = 'apache-coyote'
    homepage = 'http://httpd.apache.org/'
    matchers = [
        {'header': ('Server', 'Apache-Coyote/(?P<version>[0-9\.]+)')},
    ]


class ApacheModbwlimitedPlugin(Plugin):
    name = 'apache-mod_bwlimited'
    homepage = 'http://cpanel.com/'  # It comes with cpanel
    matchers = [
        {'header': ('Server', 'mod_bwlimited/(?P<version>[0-9\.]+)')},
    ]


class ApacheModfcgidPlugin(Plugin):
    name = 'apache-mod_fcgid'
    homepage = 'https://httpd.apache.org/mod_fcgid/'
    matchers = [
        {'header': ('Server', 'mod_fcgid/(?P<version>[0-9\.]+)')},
    ]
