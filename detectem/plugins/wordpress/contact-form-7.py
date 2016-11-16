from detectem.plugin import Plugin


class ContactForm7Plugin(Plugin):
    name = 'contact-form-7'
    homepage = 'http://contactform7.com/'

    matchers = [
        {'url': '/contact-form-7/includes/js/scripts\.js\?ver=(?P<version>[0-9\.]+)'},
    ]
