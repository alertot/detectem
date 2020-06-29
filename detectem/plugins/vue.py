from detectem.plugin import Plugin


class VuePlugin(Plugin):
    name = "vue"
    homepage = "https://vuejs.org"
    vendor = "Evan You"
    tags = ["vue", "js framework"]
    matchers = [
        {"url": r"/vue@(?P<version>[0-9a-z\.-]+)"},
        {"dom": ("window.Vue", "window.Vue.version")},
        {"xpath": ("//*[contains(local-name(@*),'data-v-')]", None)},
    ]
