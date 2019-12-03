from detectem.plugin import Plugin


class EmberJSPlugin(Plugin):
    name = "ember"
    homepage = "http://emberjs.com"
    tags = ["ember", "javascript", "js framework"]

    matchers = [{"dom": ("window.Ember", "window.Ember.VERSION")}]
