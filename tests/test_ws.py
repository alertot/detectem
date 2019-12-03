import json

from unittest.mock import patch

from boddle import boddle

from detectem.exceptions import NoPluginsError, SplashError
from detectem.ws import do_detection


"""
Tests run with `autospec` to match function signature in case of change
"""


@patch("detectem.ws.get_detection_results", autospec=True)
def test_do_detection_with_normal_behavior(gdr):
    gdr.return_value = []

    with boddle(method="post", params={"url": "http://domain.tld"}):
        assert do_detection() == json.dumps([])


@patch("detectem.ws.get_detection_results", autospec=True)
def test_do_detection_with_splash_exception(gdr):
    gdr.side_effect = SplashError("splash")

    with boddle(method="post", params={"url": "http://domain.tld"}):
        assert do_detection() == json.dumps({"error": "Splash error: splash"})


@patch("detectem.ws.get_detection_results", autospec=True)
def test_do_detection_with_noplugins_exception(gdr):
    gdr.side_effect = NoPluginsError("No plugins")

    with boddle(method="post", params={"url": "http://domain.tld"}):
        assert do_detection() == json.dumps({"error": "No plugins"})
