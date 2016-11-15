import pytest


def pytest_addoption(parser):
    parser.addoption("--plugin", action="store", default=None)


@pytest.fixture
def plugin(request):
    return request.config.getoption("--plugin")
