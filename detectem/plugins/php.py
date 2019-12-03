from detectem.plugin import Plugin


class PhpPlugin(Plugin):
    name = "php"
    homepage = "http://php.net/"
    tags = ["php"]

    matchers = [{"header": ("X-Powered-By", r"PHP/(?P<version>[0-9\.]+)")}]
