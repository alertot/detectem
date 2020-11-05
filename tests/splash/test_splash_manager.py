from unittest.mock import patch

import pytest

from detectem.splash import (
    DockerSplashManager,
    RemoteSplashManager,
    SplashManagerInterface,
    get_splash_manager,
    requests,
)


@pytest.mark.parametrize(
    "value,klass", [(True, DockerSplashManager), (False, RemoteSplashManager)]
)
def test_get_splash_manager(value, klass):
    with patch("detectem.splash.NUMBER_OF_SPLASH_INSTANCES", 1):
        with patch("detectem.splash.SETUP_SPLASH", value):
            splash_instance = get_splash_manager()
            assert isinstance(splash_instance, klass)


class TestSplashManagerInterface:
    def test_assign_instance_valid_case(self):
        class TestManager(SplashManagerInterface):
            handle_error = lambda v: v
            setup = lambda v: v
            teardown = lambda v: v

        tm = TestManager()
        # Set manager metadata
        container_name = "c-1"
        url = "http://localhost"
        tm._instances[container_name] = {"url": url, "in_use": False}

        # Mock requests response
        class PingResponse:
            status_code = 200

        with patch.object(requests, "get", return_value=lambda u: PingResponse()):
            with tm.assign_instance() as (c, u):
                assert c == container_name
                assert u == url
                assert tm._instances[container_name]["in_use"]

        assert not tm._instances[container_name]["in_use"]
