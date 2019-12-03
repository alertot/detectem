from detectem.plugin import Plugin


class WebpackPlugin(Plugin):
    name = "webpack"
    homepage = "https://webpack.js.org/"
    tags = ["webpack", "module bundler"]

    matchers = [{"dom": ("window.webpackJsonp", None)}]
