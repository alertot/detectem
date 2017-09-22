from detectem.plugin import Plugin


class LightBoxPlugin(Plugin):
    name = 'lightbox'
    homepage = 'http://lokeshdhakar.com/projects/lightbox2/'
    matchers = [
        {'body': '\* Lightbox v(?P<version>[0-9\.]+).*Lokesh Dhakar'},
        {'url': '/lightbox2/(?P<version>[0-9\.]+)/js/lightbox(\.min)?\.(js|css)'},
    ]
    indicators = [
        {'url': '/lightbox2/([^/]+/)*lightbox(\.min)?\.(js|css)'},
    ]


class PrettyPhotoPlugin(Plugin):
    name = 'prettyphoto'
    homepage = 'http://www.no-margin-for-errors.com/projects/prettyphoto-jquery-lightbox-clone/'  # noqa: E501
    matchers = [
        {'body': 'prettyPhoto\s*=\s*{version:\s*[\'"](?P<version>[0-9\.]+)[\'"]}'},
        {'url': '/prettyPhoto/(?P<version>[0-9\.]+)/css/prettyPhoto(\.min)?\.css'},
        {'url': '/prettyPhoto/(?P<version>[0-9\.]+)/js/jquery\.prettyPhoto(\.min)?\.js'},
    ]
