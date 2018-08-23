from detectem.plugin import Plugin


class NewsShowProGk5Plugin(Plugin):
    name = 'news-show-pro-gk5'
    homepage = 'https://www.gavick.com/news-show-pro'
    tags = ['joomla!']

    matchers = [
        {'body': r'\* @package News Show Pro GK5\n'},
    ]
    hints = ["joomla!"]
