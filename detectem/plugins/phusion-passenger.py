from detectem.plugin import Plugin


class PhusionPassengerPlugin(Plugin):
    name = "phusion-passenger"
    homepage = "https://www.phusionpassenger.com/"
    tags = ["web server"]

    matchers = [{"header": ("Server", r"Phusion_Passenger/(?P<version>[0-9\.]+)")}]
