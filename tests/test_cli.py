import pytest

from detectem.cli import get_detection_results
from detectem.exceptions import NoPluginsError, SplashError


def test_get_detection_results_with_no_plugins(mocker):
    mocker.patch("detectem.cli.load_plugins", return_value=[])

    with pytest.raises(NoPluginsError):
        get_detection_results("http://domain.tld", timeout=30, metadata=True)


def test_get_detection_results_with_splash_error(mocker):
    mocker.patch("detectem.cli.get_response", side_effect=SplashError("test"))

    with pytest.raises(SplashError):
        get_detection_results("http://domain.tld", timeout=30, metadata=True)


def test_get_detection_ok(mocker):
    class FakeDetector:
        def __init__(*args):
            pass

        def get_results(**kwargs):
            return [1, 2, 3]

    mocker.patch("detectem.cli.get_response", return_value=1)
    mocker.patch("detectem.cli.Detector", return_value=FakeDetector)

    rs = get_detection_results("http://domain.tld", timeout=30, metadata=True)
    assert rs == {"url": "http://domain.tld", "softwares": [1, 2, 3]}
