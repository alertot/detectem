from detectem.plugin import Plugin


class ContactForm7Plugin(Plugin):
    name = 'contact-form-7'
    homepage = 'http://contactform7.com/'
    tags = ['wordpress']

    indicators = [
        {'url': r'/contact-form-7/includes/js/scripts\.js'},
    ]
