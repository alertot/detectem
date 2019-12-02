class DockerStartError(Exception):
    pass


class NotNamedParameterFound(Exception):
    pass


class SplashError(Exception):
    def __init__(self, msg):
        self.msg = "Splash error: {}".format(msg)
        super().__init__(self.msg)


class NoPluginsError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)
