from detectem.plugin import Plugin


class NginxPlugin(Plugin):
    name = "nginx"
    homepage = "https://www.nginx.com/"
    vendor = "NGINX"
    tags = ["web server", "nginx"]

    matchers = [
        {"header": ("Server", r"nginx/(?P<version>[0-9\.]+)")},
        {"header": ("Server", r"nginx\s*")},
    ]
