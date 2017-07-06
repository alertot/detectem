import pytest

from detectem.core import Detector, Result
from detectem.plugin import Plugin


class TestDetector():
    HAR_ENTRY_1 = {
        'request': {
            'url': 'http://domain.tld/libA-1.4.2.js'
        },
        'response': {
            'url': 'http://domain.tld/libA-1.4.2.js'
        },
    }

    @pytest.fixture
    def min_detector(self):
        return Detector({'har': None, 'softwares': None}, [], None)

    def test_detector_starts_with_empty_results(self):
        d = Detector({'har': None, 'softwares': None}, [], None)
        assert not d._results

    @pytest.mark.parametrize('entry,result', [
        ({'request': {'url': 'http://a'}}, 'http://a'),
        ({
            'request': {'url': 'http://a'},
            'response': {'url': 'http://b'},
        }, 'http://b'),

    ])
    def test_get_url(self, entry, result):
        assert Detector.get_url(entry) == result

    def test_get_hints_with_valid_hint(self, min_detector):
        class TestPlugin(Plugin):
            name = 'bla'
            hints = [lambda v: Result('test')]

        hints = min_detector.get_hints(TestPlugin, {})
        assert hints

    def test_get_hints_with_invalid_hint(self, min_detector):
        class TestPlugin(Plugin):
            name = 'bla'
            hints = [lambda v: 'test']

        hints = min_detector.get_hints(TestPlugin, {})
        assert not hints
