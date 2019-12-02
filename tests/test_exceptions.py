from detectem.exceptions import SplashError


def test_splash_error():
    try:
        raise SplashError("test")
    except SplashError as e:
        assert "Splash error: test" in str(e)
