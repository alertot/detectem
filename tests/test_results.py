import pytest

from detectem.results import Result, ResultCollection
from detectem.settings import GENERIC_TYPE, HINT_TYPE, INDICATOR_TYPE


class TestResultCollection:
    @staticmethod
    def _assert_results(detected, results):
        c = ResultCollection()
        for d in detected:
            c.add_result(d)
        assert set(c.get_results()) == set(results)

    @pytest.mark.parametrize(
        "detected,results",
        [
            (
                [
                    Result("pluginA", "1.1"),
                    Result("pluginB", "3.8.7"),
                    Result("pluginC", "4.0"),
                ],
                [
                    Result("pluginA", "1.1"),
                    Result("pluginB", "3.8.7"),
                    Result("pluginC", "4.0"),
                ],
            ),
            (
                [
                    Result("pluginA", "1.3"),
                    Result("pluginA", "1.2"),
                    Result("pluginA", "1.1"),
                ],
                [
                    Result("pluginA", "1.1"),
                    Result("pluginA", "1.2"),
                    Result("pluginA", "1.3"),
                ],
            ),
            (
                [
                    Result("pluginA", "1.1"),
                    Result("pluginC", type=HINT_TYPE),
                    Result("pluginB", type=INDICATOR_TYPE),
                    Result("pluginD", type=GENERIC_TYPE),
                ],
                [
                    Result("pluginA", "1.1"),
                    Result("pluginB", type=INDICATOR_TYPE),
                    Result("pluginC", type=HINT_TYPE),
                    Result("pluginD", type=GENERIC_TYPE),
                ],
            ),
        ],
    )
    def test_get_all_detected_plugins(self, detected, results):
        self._assert_results(detected, results)

    @pytest.mark.parametrize(
        "detected,results",
        [
            (
                [
                    Result("pluginA", "1.1"),
                    Result("pluginA", "1.2"),
                    Result("pluginA", "1.1"),
                ],
                [Result("pluginA", "1.1"), Result("pluginA", "1.2")],
            ),
            (
                [
                    Result("pluginA", "1.1"),
                    Result("pluginA", type=INDICATOR_TYPE),
                    Result("pluginA", type=HINT_TYPE),
                ],
                [Result("pluginA", "1.1")],
            ),
            (
                [Result("pluginB", type=HINT_TYPE), Result("pluginB", type=HINT_TYPE)],
                [Result("pluginB", type=HINT_TYPE)],
            ),
            (
                [
                    Result("pluginB", type=INDICATOR_TYPE),
                    Result("pluginB", type=INDICATOR_TYPE),
                ],
                [Result("pluginB", type=INDICATOR_TYPE)],
            ),
            (
                [
                    Result("pluginB", type=INDICATOR_TYPE),
                    Result("pluginB", type=HINT_TYPE),
                ],
                [Result("pluginB", type=INDICATOR_TYPE)],
            ),
            (
                [
                    Result("pluginB", type=INDICATOR_TYPE),
                    Result("pluginB", type=GENERIC_TYPE),
                ],
                [Result("pluginB", type=INDICATOR_TYPE)],
            ),
        ],
    )
    def test_remove_duplicated_results(self, detected, results):
        self._assert_results(detected, results)
