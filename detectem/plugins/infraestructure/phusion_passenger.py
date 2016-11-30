from detectem.plugin import Plugin


class PhusionPassengerPlugin(Plugin):
    name = 'phusion_passenger'
    homepage = 'https://www.phusionpassenger.com/'
    matchers = [
        {'header': ('Server', 'Phusion_Passenger/(?P<version>[0-9\.]+)')},
    ]
