import pytest

from detectem.core import Detector, Result, ResultCollection
from detectem.plugin import Plugin, PluginCollection
from detectem.settings import INDICATOR_TYPE, HINT_TYPE, MAIN_ENTRY
from detectem.plugins.helpers import meta_generator


class TestDetector():
    HAR_ENTRY_1 = {
        'request': {
            'url': 'http://domain.tld/libA-1.4.2.js'
        },
        'response': {
            'url': 'http://domain.tld/libA-1.4.2.js'
        },
    }

    HAR_NO_URL_REDIRECT = [
        {
            'request': {'url': 'http://domain.tld/'},
            'response': {},
        },
        {
            'request': {'url': 'http://domain.tld/js/script.js'},
            'response': {},
        }
    ]
    HAR_URL_REDIRECT_PATH = [
        {
            'request': {'url': 'http://domain.tld/'},
            'response': {'headers': [
                {'name': 'Location', 'value': '/new/default.html'}
            ]},
        },
        {
            'request': {'url': 'http://domain.tld/new/default.html'},
            'response': {},
        }
    ]
    HAR_URL_REDIRECT_ABS = [
        {
            'request': {'url': 'http://domain.tld/'},
            'response': {'headers': [
                {'name': 'Location', 'value': 'http://other-domain.tld/'}
            ]},
        },
        {
            'request': {'url': 'http://other-domain.tld/'},
            'response': {},
        }
    ]

    URL = 'http://domain.tld/'

    FOO_PLUGIN = {
        'name': 'foo',
        'homepage': 'foo',
        'matchers': {
            'url': 'foo.*-(?P<version>[0-9\.]+)\.js',
            'header': ('FooHeader', 'Foo.* v(?P<version>[0-9\.]+)'),
            'body': 'Foo.* v(?P<version>[0-9\.]+)',
            'xpath': (meta_generator('foo-min'), '(?P<version>[0-9\.]+)'),
        },
        'indicators': {
            'url': 'foo.*\.js',
            'header': ('FooHeader', 'Foo'),
            'body': 'Foo',
            'xpath': "//meta[@name='generator']",
        },
        'modular_matchers': {
            'url': 'foo-(?P<name>\w+)-.*\.js',
            'header': ('FooHeader', 'Foo-(?P<name>\w+)'),
            'body': 'Foo-(?P<name>\w+)',
            'xpath': (meta_generator('foo-min'), 'foo-(?P<name>\w+)'),
        },
    }

    FOO_RESULTS = [
        [{'name': 'foo', 'version': '1.1'}],
        [{'name': 'foo'}],
        [{'name': 'foo-min', 'version': '1.1'}],
    ]

    MATCHER_SOURCES = [
        ['matchers'],
        ['indicators'],
        ['matchers', 'modular_matchers'],
    ]

    def test_detector_starts_with_empty_results(self):
        d = Detector({'har': None, 'softwares': None}, [], None)
        assert not d._results.get_results()

    @pytest.mark.parametrize("har,index", [
        (HAR_NO_URL_REDIRECT, 0),
        (HAR_URL_REDIRECT_PATH, 1),
        (HAR_URL_REDIRECT_ABS, 1),
    ])
    def test_mark_main_entry(self, har, index):
        d = self._create_detector(har, [])
        assert d.har[index]['detectem']['type'] == MAIN_ENTRY

    def test_convert_inline_script_to_har_entry(self):
        script = 'Inline script'

        d = Detector({'har': [], 'softwares': [], 'scripts': [script]}, None, self.URL)
        e = d.har[0]

        assert e['request']['url'] == self.URL
        assert e['response']['content']['text'] == script

    @pytest.mark.parametrize("scripts,n_entries", [
        ([], 0),
        (['script1', 'script2'], 2),
    ])
    def test_add_inline_scripts_to_har(self, scripts, n_entries):
        d = Detector({'har': [], 'softwares': [], 'scripts': scripts}, None, self.URL)
        assert len(d.har) == n_entries

    def _create_plugin(self, template, sources, matchers):
        class TestPlugin(Plugin):
            name = template['name']
            homepage = template['homepage']

        p = TestPlugin()
        for s in sources:
            g = [{m: template[s][m]} for m in matchers]
            setattr(p, s, g)
        return p

    def _create_detector(self, har, plugins):
        pc = PluginCollection()
        for p in plugins:
            pc.add(p)
        return Detector({'har': har, 'softwares': []}, pc, self.URL)

    @pytest.mark.parametrize('sources,result', zip(MATCHER_SOURCES, FOO_RESULTS))
    def test_match_from_headers(self, sources, result):
        har = [
            {
                'request': {'url': self.URL},
                'response': {
                    'url': self.URL,
                    'headers': [
                        {'name': 'FooHeader', 'value': 'Foo-min v1.1'}
                    ]
                },
            },
        ]
        p = self._create_plugin(self.FOO_PLUGIN, sources, ['header'])
        d = self._create_detector(har, [p])

        assert d.get_results() == result

    @pytest.mark.parametrize('sources', MATCHER_SOURCES)
    def test_match_from_headers_ignores_resource_entries(self, sources):
        har = [
            {
                'request': {'url': self.URL},
                'response': {
                    'url': self.URL,
                    'headers': [],
                },
            },
            {
                'request': {'url': 'http://foo.org/lib/foo.js'},
                'response': {
                    'url': 'http://foo.org/lib/foo.js',
                    'headers': [
                        {'name': 'FooHeader', 'value': 'Foo-min v1.1'}
                    ]
                },
            },
        ]
        p = self._create_plugin(self.FOO_PLUGIN, sources, ['header'])
        d = self._create_detector(har, [p])

        assert not d.get_results()

    @pytest.mark.parametrize('sources,result', zip(MATCHER_SOURCES, FOO_RESULTS))
    def test_match_from_body(self, sources, result):
        har = [
            {
                'request': {'url': self.URL},
                'response': {
                    'url': self.URL,
                    'content': {'text': 'Main content'},
                },
            },
            {
                'request': {'url': 'http://foo.org/lib/foo.js'},
                'response': {
                    'url': 'http://foo.org/lib/foo.js',
                    'content': {'text': 'Plugin Foo-min v1.1'},
                },
            },
        ]
        p = self._create_plugin(self.FOO_PLUGIN, sources, ['body'])
        d = self._create_detector(har, [p])

        assert d.get_results() == result

    @pytest.mark.parametrize('sources', MATCHER_SOURCES)
    def test_match_from_body_excludes_main_entry(self, sources):
        har = [
            {
                'request': {'url': self.URL},
                'response': {
                    'url': self.URL,
                    'content': {'text': 'About Foo-min v1.1'},
                },
            },
        ]
        p = self._create_plugin(self.FOO_PLUGIN, sources, ['body'])
        d = self._create_detector(har, [p])

        assert not d.get_results()

    @pytest.mark.parametrize('sources,result', zip(MATCHER_SOURCES, FOO_RESULTS))
    def test_match_from_url(self, sources, result):
        har = [
            {
                'request': {'url': self.URL},
                'response': {'url': self.URL},
            },
            {
                'request': {'url': 'http://foo.org/lib/foo-min-1.1.js'},
                'response': {
                    'url': 'http://foo.org/lib/foo-min-1.1.js',
                },
            },
        ]
        p = self._create_plugin(self.FOO_PLUGIN, sources, ['url'])
        d = self._create_detector(har, [p])

        assert d.get_results() == result

    @pytest.mark.parametrize('sources,result', zip(MATCHER_SOURCES, FOO_RESULTS))
    def test_match_from_xpath(self, sources, result):
        har = [
            {
                'request': {'url': self.URL},
                'response': {
                    'url': self.URL,
                    'content': {
                        'text': '<meta name="generator" content="foo-min 1.1">'
                    },
                },
            },
        ]
        p = self._create_plugin(self.FOO_PLUGIN, sources, ['xpath'])
        d = self._create_detector(har, [p])

        assert d.get_results() == result

    def test_get_hints_with_valid_hint(self):
        class TestPlugin(Plugin):
            name = 'test'
            homepage = 'test'

        class BlaPlugin(Plugin):
            name = 'bla'
            hints = ['test']

        detector = self._create_detector(None, [TestPlugin()])

        hints = detector.get_hints(BlaPlugin())
        assert hints

    def test_get_hints_with_invalid_hint(self):
        class BlaPlugin(Plugin):
            name = 'bla'
            hints = ['test']

        detector = self._create_detector(None, [])
        hints = detector.get_hints(BlaPlugin())
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
