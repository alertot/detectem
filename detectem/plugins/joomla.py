from detectem.plugin import Plugin


class JoomlaPlugin(Plugin):
    name = "joomla!"
    homepage = "https://www.joomla.org/"
    vendor = "Open Source Matters, Inc."
    tags = ["joomla!", "cms", "php"]

    matchers = [
        {
            "body": '<meta name="generator" content="Joomla! - Open Source Content Management"'
        }
    ]
