from unittest.mock import patch

from detectem.settings import get_boolean_value


def test_get_boolean_value_with_true():
    with patch.dict("os.environ", {"test": "True"}):
        assert get_boolean_value("test", False)


def test_get_boolean_value_with_false():
    with patch.dict("os.environ", {"test": "False"}):
        assert not get_boolean_value("test", True)


def test_get_boolean_value_with_default():
    with patch.dict("os.environ", {"test": "xxx"}):
        assert get_boolean_value("test", "default") == "default"
