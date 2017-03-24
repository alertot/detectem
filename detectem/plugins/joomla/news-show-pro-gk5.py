from detectem.plugin import Plugin
from detectem.core import Result
from detectem.plugins.joomla.joomla import JoomlaPlugin


class NewsShowProGk5Plugin(Plugin):
    name = 'news-show-pro-gk5'
    homepage = 'https://www.gavick.com/news-show-pro'
    indicators = [
        {'body': '\* @package News Show Pro GK5\n'},
    ]
    hints = [
        lambda entry: Result(JoomlaPlugin.name, homepage=JoomlaPlugin.homepage)
    ]
