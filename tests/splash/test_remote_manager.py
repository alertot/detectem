from unittest.mock import patch

import pytest

from detectem.splash import RemoteSplashManager


class TestRemoteSplashManager:
    def test_init_with_invalid_settings(self):
        with pytest.raises(ValueError):
            RemoteSplashManager()

    def test_init(self):
        with patch("detectem.splash.NUMBER_OF_SPLASH_INSTANCES", 1):
            RemoteSplashManager()

    def test_setup(self):
        with patch("detectem.splash.NUMBER_OF_SPLASH_INSTANCES", 1):
            rm = RemoteSplashManager()
            rm.setup(n_instances=1)

            assert "instance-0" in rm._instances.keys()
