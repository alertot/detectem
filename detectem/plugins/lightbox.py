from detectem.plugin import Plugin


class LightBoxPlugin(Plugin):
    name = "lightbox"
    homepage = "http://lokeshdhakar.com/projects/lightbox2/"
    tags = ["javascript"]

    matchers = [
        {"body": r"\* Lightbox v(?P<version>[0-9\.]+).*Lokesh Dhakar"},
        {"url": r"/lightbox2/(?P<version>[0-9\.]+)/js/lightbox(\.min)?\.(js|css)"},
        {"url": r"/lightbox2/([^/]+/)*lightbox(\.min)?\.(js|css)"},
    ]


class PrettyPhotoPlugin(Plugin):
    name = "prettyphoto"
    homepage = "http://www.no-margin-for-errors.com/projects/prettyphoto-jquery-lightbox-clone/"  # noqa: E501
    tags = ["javascript"]

    matchers = [
        {"body": r'prettyPhoto\s*=\s*{version:\s*[\'"](?P<version>[0-9\.]+)[\'"]}'},
        {"url": r"/prettyPhoto/(?P<version>[0-9\.]+)/css/prettyPhoto(\.min)?\.css"},
        {
            "url": r"/prettyPhoto/(?P<version>[0-9\.]+)/js/jquery\.prettyPhoto(\.min)?\.js"
        },
    ]
