import pytest

from detectem.core import HarProcessor
from detectem.settings import INLINE_SCRIPT_ENTRY, MAIN_ENTRY


class TestHarProcessor:
    HAR_NO_URL_REDIRECT = [
        {"request": {"url": "http://domain.tld/"}, "response": {}},
        {"request": {"url": "http://domain.tld/js/script.js"}, "response": {}},
    ]

    HAR_URL_REDIRECT = [
        {
            "request": {"url": "http://domain.tld/"},
            "response": {
                "headers": [{"name": "Location", "value": "/new/default.html"}]
            },
        },
        {"request": {"url": "http://domain.tld/new/default.html"}, "response": {}},
    ]

    def test__set_entry_type(self):
        data = {}
        HarProcessor._set_entry_type(data, "marker")
        assert data["detectem"]["type"] == "marker"

    @pytest.mark.parametrize(
        "entry,result",
        [
            ({"response": {}}, None),
            ({"response": {"headers": [{"name": "any"}]}}, None),
            (HAR_URL_REDIRECT[0], "/new/default.html"),
        ],
    )
    def test__get_location(self, entry, result):
        assert HarProcessor._get_location(entry) == result

    def test__script_to_har_entry(self):
        url = "http://url"
        content = "content"

        entry = HarProcessor._script_to_har_entry(content, url)
        assert entry["request"]["url"] == url
        assert entry["response"]["url"] == url
        assert entry["response"]["content"]["text"] == content

        assert entry["detectem"]["type"] == INLINE_SCRIPT_ENTRY

    @pytest.mark.parametrize(
        "entries,index", [(HAR_NO_URL_REDIRECT, 0), (HAR_URL_REDIRECT, 1)]
    )
    def test_mark_entries(self, entries, index):
        HarProcessor().mark_entries(entries)
        assert entries[index]["detectem"]["type"] == MAIN_ENTRY
