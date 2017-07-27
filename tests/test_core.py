import pytest

from detectem.core import Detector, Result, ResultCollection
from detectem.plugin import Plugin
from detectem.settings import INDICATOR_TYPE, HINT_TYPE


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
        assert not d._results.get_results()

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


class TestResultCollection():

    @staticmethod
    def _assert_results(detected, results):
        c = ResultCollection()
        for d in detected:
            c.add_result(d)
        assert set(c.get_results()) == set(results)

    @pytest.mark.parametrize('detected,results', [
        ([
            Result('pluginA', '1.1'),
            Result('pluginB', '3.8.7'),
            Result('pluginC', '4.0'),
         ],
         [
            Result('pluginA', '1.1'),
            Result('pluginB', '3.8.7'),
            Result('pluginC', '4.0'),
         ]),

        ([
            Result('pluginA', '1.3'),
            Result('pluginA', '1.2'),
            Result('pluginA', '1.1'),
         ],
         [
            Result('pluginA', '1.1'),
            Result('pluginA', '1.2'),
            Result('pluginA', '1.3'),
         ]),

        ([
            Result('pluginA', '1.1'),
            Result('pluginC', type=HINT_TYPE),
            Result('pluginB', type=INDICATOR_TYPE),
         ],
         [
            Result('pluginA', '1.1'),
            Result('pluginB', type=INDICATOR_TYPE),
            Result('pluginC', type=HINT_TYPE),
         ]),
    ])
    def test_get_all_detected_plugins(self, detected, results):
        self._assert_results(detected, results)

    @pytest.mark.parametrize('detected,results', [
        ({
            Result('pluginA', '1.1'),
            Result('pluginA', '1.2'),
            Result('pluginA', '1.1'),
         },
         {
            Result('pluginA', '1.1'),
            Result('pluginA', '1.2'),
         }),

        ({
            Result('pluginA', '1.1'),
            Result('pluginA', type=INDICATOR_TYPE),
            Result('pluginA', type=HINT_TYPE),
         },
         {
            Result('pluginA', '1.1'),
         }),

        ({Result('pluginB', type=HINT_TYPE), Result('pluginB', type=HINT_TYPE)},
         {Result('pluginB', type=HINT_TYPE)}),

        ({Result('pluginB', type=INDICATOR_TYPE), Result('pluginB', type=INDICATOR_TYPE)},
         {Result('pluginB', type=INDICATOR_TYPE)}),

        ({Result('pluginB', type=INDICATOR_TYPE), Result('pluginB', type=HINT_TYPE)},
         {Result('pluginB', type=INDICATOR_TYPE)}),
     ])
    def test_remove_duplicated_results(self, detected, results):
        self._assert_results(detected, results)
