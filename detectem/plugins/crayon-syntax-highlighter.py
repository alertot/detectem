from detectem.plugin import Plugin


class CrayonSyntaxHighlighterPlugin(Plugin):
    name = 'crayon-syntax-highlighter'
    homepage = 'https://wordpress.org/plugins-wp/crayon-syntax-highlighter/'
    tags = ['wordpress']
    js_matchers = [
        {
            'check': 'window.CrayonSyntaxSettings',
            'version': 'window.CrayonSyntaxSettings.version',
        },
    ]
