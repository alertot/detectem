from detectem.plugin import Plugin


class IISPlugin(Plugin):
    name = "iis"
    homepage = "https://www.iis.net/"
    tags = ["web server", "iis"]

    matchers = [{"header": ("Server", r"Microsoft-IIS/(?P<version>[0-9\.]+)")}]
