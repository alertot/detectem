import pytest

from detectem.utils import get_url


@pytest.mark.parametrize(
    "entry,result",
    [
        ({"request": {"url": "http://a"}}, "http://a"),
        ({"request": {"url": "http://a"}, "response": {"url": "http://b"}}, "http://b"),
    ],
)
def test_get_url(entry, result):
    assert get_url(entry) == result
