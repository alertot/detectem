import re
import inspect
import logging
import glob

from importlib.util import find_spec, module_from_spec

from zope.interface import implementer, Interface, Attribute
from zope.interface.verify import verifyObject
from zope.interface.exceptions import BrokenImplementation

from detectem.settings import PLUGIN_PACKAGES

logger = logging.getLogger('detectem')


class PluginCollection(object):

    def __init__(self):
        self._plugins = {}

    def __len__(self):
        return len(self._plugins)

    def add(self, ins):
        self._plugins[ins.name] = ins

    def get(self, name):
        return self._plugins.get(name)

    def get_all(self):
        return self._plugins.values()

    def with_version_matchers(self):
        return [p for p in self._plugins.values() if not p.is_indicator]

    def with_indicator_matchers(self):
        return [p for p in self._plugins.values() if p.is_indicator]

    def with_js_matchers(self):
        return [p for p in self._plugins.values() if hasattr(p, 'js_matchers')]


class _PluginLoader(object):

    def __init__(self):
        self.plugins = PluginCollection()

    def _full_class_name(self, ins):
        return '{}.{}'.format(ins.__class__.__module__, ins.__class__.__name__)

    def _get_plugin_module_paths(self, plugin_dir):
        filepaths = [
            fp for fp in glob.glob('{}/**/*.py'.format(plugin_dir), recursive=True)
            if not fp.endswith('__init__.py')
        ]
        rel_paths = [re.sub(plugin_dir.rstrip('/') + '/', '', fp) for fp in filepaths]
        module_paths = [rp.replace('/', '.').replace('.py', '') for rp in rel_paths]
        return module_paths

    def _load_plugin(self, klass):
        ins = klass()
        try:
            if verifyObject(IPlugin, ins):
                reg = self.plugins.get(ins.name)
                if not reg:
                    self.plugins.add(ins)
                else:
                    logger.warning(
                        "Plugin '%(name)s' by '%(ins)s' is already provided by '%(reg)s'",
                        {'name': ins.name,
                         'ins': self._full_class_name(ins),
                         'reg': self._full_class_name(reg)}
                    )
        except BrokenImplementation:
            logger.warning(
                "Plugin '%(name)s' doesn't provide the plugin interface",
                {'name': self._full_class_name(ins)}
            )

    def load_plugins(self, plugins_package):
        try:
            # Resolve directory in the filesystem
            plugin_dir = find_spec(plugins_package).submodule_search_locations[0]
        except ImportError:
            logger.debug(
                "[+] Could not load plugins package '%(pkg)s'",
                {'pkg': plugins_package}
                )
            return

        for module_path in self._get_plugin_module_paths(plugin_dir):
            # Load the module dynamically
            spec = find_spec('{}.{}'.format(plugins_package, module_path))
            m = module_from_spec(spec)
            spec.loader.exec_module(m)

            # Get classes from module and extract the plugin classes
            classes = inspect.getmembers(m, predicate=inspect.isclass)
            for _, klass in classes:
                if klass.__module__ != spec.name:
                    continue
                if not klass.__name__.endswith('Plugin'):
                    continue
                self._load_plugin(klass)


def load_plugins():
    """ Return the list of plugin instances """
    loader = _PluginLoader()
    for pkg in PLUGIN_PACKAGES:
        loader.load_plugins(pkg)
    return loader.plugins


class IPlugin(Interface):
    name = Attribute(""" Name to identify the plugin. """)
    homepage = Attribute(""" Plugin homepage. """)


@implementer(IPlugin)
class Plugin():
    def _get_matchers(self, value, source='matchers'):
        matchers_dict = getattr(self, source, [])
        return [m[value] for m in matchers_dict if value in m]

    def get_grouped_matchers(self, source='matchers'):
        """ Return dictionary of matchers (not empty ones) """
        data = {}
        for k in ['url', 'body', 'header']:
            m = self._get_matchers(k, source)
            if m:
                data[k] = m

        return data

    @property
    def is_modular(self):
        return bool(hasattr(self, 'modular_matchers'))

    @property
    def is_indicator(self):
        return bool(hasattr(self, 'indicators'))
