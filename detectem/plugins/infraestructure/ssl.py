from detectem.plugin import Plugin


class ModSSLPlugin(Plugin):
    name = 'modssl'
    matchers = [
        {'header': ('Server', 'mod_ssl/(?P<version>[0-9\.]+)')},
    ]


class OpenSSLPlugin(Plugin):
    name = 'openssl'
    matchers = [
        {'header': ('Server', 'OpenSSL/(?P<version>[\w\.]+)')},
    ]
