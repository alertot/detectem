from detectem.plugin import Plugin


class W3TotalCachePlugin(Plugin):
    name = 'w3-total-cache'
    homepage = 'https://wordpress.org/plugins/w3-total-cache/'
    tags = ['wordpress']

    matchers = [
        {'header': ('X-Powered-By', r'W3 Total Cache/(?P<version>[0-9\.]+)')},
    ]
