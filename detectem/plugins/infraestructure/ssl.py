from detectem.plugin import Plugin


class ModSSLPlugin(Plugin):
    name = 'modssl'
    homepage = 'http://www.modssl.org/'
    matchers = [
        {'header': ('Server', 'mod_ssl/(?P<version>[0-9\.]+)')},
    ]


class OpenSSLPlugin(Plugin):
    name = 'openssl'
    homepage = 'https://www.openssl.org/'
    matchers = [
        {'header': ('Server', 'OpenSSL/(?P<version>[\w\.]+)')},
    ]
