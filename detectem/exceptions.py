class DockerStartError(Exception):
    pass


class NotNamedParameterFound(Exception):
    pass


class SplashError(Exception):
    def __init__(self, msg):
        msg = 'Splash error: {}'.format(msg)
        super().__init__(msg)


class NoPluginsError(Exception):
    pass
