from detectem.plugin import Plugin


class JoomlaPlugin(Plugin):
    name = 'joomla'
    homepage = 'https://www.joomla.org/'
    tags = ['joomla']

    indicators = [
        {
            'body':
                '<meta name="generator" content="Joomla! - Open Source Content Management"'
        },
    ]
