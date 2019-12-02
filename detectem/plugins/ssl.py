from detectem.plugin import Plugin


class ModSSLPlugin(Plugin):
    name = "modssl"
    homepage = "http://www.modssl.org/"
    tags = ["ssl"]

    matchers = [{"header": ("Server", r"mod_ssl/(?P<version>[0-9\.]+)")}]


class OpenSSLPlugin(Plugin):
    name = "openssl"
    homepage = "https://www.openssl.org/"
    tags = ["ssl"]

    matchers = [{"header": ("Server", r"OpenSSL/(?P<version>[\w\.]+)")}]
