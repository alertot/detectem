from collections import defaultdict
from distutils.version import LooseVersion

from detectem.settings import GENERIC_TYPE, HINT_TYPE, INDICATOR_TYPE, VERSION_TYPE


class Result:
    def __init__(
        self,
        name,
        version=None,
        homepage=None,
        from_url=None,
        type=VERSION_TYPE,
        plugin=None,
    ):
        self.name = name
        self.type = type
        self.version = version
        self.homepage = homepage
        self.from_url = from_url
        self.plugin = plugin

    def __hash__(self):
        return hash((self.name, self.version, self.type))

    def __eq__(self, o):
        def to_tuple(rt):
            return (rt.name, rt.version, rt.type)

        return to_tuple(self) == to_tuple(o)

    def __lt__(self, o):
        def to_tuple(rt):
            return (rt.name, LooseVersion(rt.version or "0"), rt.type)

        return to_tuple(self) < to_tuple(o)

    def __repr__(self):
        return str({"name": self.name, "version": self.version, "type": self.type})


class ResultCollection:
    def __init__(self):
        self._results = defaultdict(list)

    def add_result(self, rt):
        self._results[rt.name].append(rt)

    def _normalize_results(self):
        norm_results = defaultdict(list)

        for p_name, p_results in self._results.items():
            rdict = defaultdict(set)
            for rt in p_results:
                rdict[rt.type].add(rt)

            p_list = []
            if VERSION_TYPE in rdict:
                p_list = list(rdict[VERSION_TYPE])
                assert len(p_list) >= 1
            elif INDICATOR_TYPE in rdict:
                p_list = list(rdict[INDICATOR_TYPE])
                assert len(p_list) == 1
            elif HINT_TYPE in rdict:
                p_list = list(rdict[HINT_TYPE])
                assert len(p_list) == 1
            elif GENERIC_TYPE in rdict:
                p_list = list(rdict[GENERIC_TYPE])
                assert len(p_list) == 1

            norm_results[p_name] = p_list

        return norm_results

    def get_results(self, normalize=True):
        results = self._normalize_results() if normalize else self._results
        return [rt for p_results in results.values() for rt in p_results]
