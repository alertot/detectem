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

LANGUAGE_TAGS = [
    'php', 'python', 'ruby', 'perl', 'node.js', 'javascript',
]
FRAMEWORK_TAGS = [
    'django', 'angular', 'backbone', 'react',
]
PRODUCT_TAGS = [
    'wordpress', 'mysql', 'jquery', 'mootools', 'apache', 'iis', 'nginx', 'ssl',
    'joomla',
]
CATEGORY_TAGS = [
    'cms', 'seo', 'blog', 'advertising networks', 'analytics', 'wiki',
    'document management system', 'miscellaneous',
    'message board', 'angular', 'js framework', 'web framework',
    'visualization', 'graphics', 'web server',
]
PLUGIN_TAGS = LANGUAGE_TAGS + FRAMEWORK_TAGS + PRODUCT_TAGS + CATEGORY_TAGS


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
        return [p for p in self._plugins.values() if p.is_version]

    def with_indicator_matchers(self):
        return [p for p in self._plugins.values() if p.is_indicator]

    def with_js_matchers(self):
        return [p for p in self._plugins.values() if p.is_js]

    def with_generic_matchers(self):
        return [p for p in self._plugins.values() if p.is_generic]


class _PluginLoader(object):
    def __init__(self):
        self.plugins = PluginCollection()

    def _full_class_name(self, ins):
        return '{}.{}'.format(ins.__class__.__module__, ins.__class__.__name__)

    def _get_plugin_module_paths(self, plugin_dir):
        ''' Return a list of every module in `plugin_dir`. '''
        filepaths = [
            fp for fp in glob.glob('{}/**/*.py'.format(plugin_dir), recursive=True)
            if not fp.endswith('__init__.py')
        ]
        rel_paths = [re.sub(plugin_dir.rstrip('/') + '/', '', fp) for fp in filepaths]
        module_paths = [rp.replace('/', '.').replace('.py', '') for rp in rel_paths]

        return module_paths

    def _is_plugin_ok(self, instance):
        ''' Return `True` if:
        1. Plugin meets plugin interface.
        2. Is not already registered in the plugin collection.
        3. Have accepted tags.

        Otherwise, return `False` and log warnings.

        '''
        try:
            verifyObject(IPlugin, instance)
        except BrokenImplementation:
            logger.warning(
                "Plugin '%(name)s' doesn't provide the plugin interface",
                {'name': self._full_class_name(instance)}
            )
            return False

        # Check if the plugin is already registered
        reg = self.plugins.get(instance.name)
        if reg:
            logger.warning(
                "Plugin '%(name)s' by '%(instance)s' is already provided by '%(reg)s'",
                {'name': instance.name,
                 'instance': self._full_class_name(instance),
                 'reg': self._full_class_name(reg)}
            )
            return False

        for tag in instance.tags:
            if tag not in PLUGIN_TAGS:
                logger.warning(
                    "Invalid tag '%(tag)s' in '%(instance)s'",
                    {'tag': tag, 'instance': self._full_class_name(instance)}
                )
                return False

        return True

    def load_plugins(self, plugins_package):
        ''' Load plugins from `plugins_package` module. '''
        try:
            # Resolve directory in the filesystem
            plugin_dir = find_spec(plugins_package).submodule_search_locations[0]
        except ImportError:
            logger.error(
                "Could not load plugins package '%(pkg)s'",
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
                # Avoid imports processing
                if klass.__module__ != spec.name:
                    continue

                # Avoid classes not ending in Plugin
                if not klass.__name__.endswith('Plugin'):
                    continue

                instance = klass()
                if self._is_plugin_ok(instance):
                    self.plugins.add(instance)


def load_plugins():
    """ Return the list of plugin instances. """
    loader = _PluginLoader()

    for pkg in PLUGIN_PACKAGES:
        loader.load_plugins(pkg)

    return loader.plugins


class IPlugin(Interface):
    name = Attribute(""" Name to identify the plugin. """)
    homepage = Attribute(""" Plugin homepage. """)
    tags = Attribute(""" Tags to categorize plugins """)


@implementer(IPlugin)
class Plugin():
    """ Class used by normal plugins.
    It implements :class:`~IPlugin`.

    """
    ptype = 'normal'

    def _get_matchers(self, mtype, source='matchers'):
        ''' Return `mtype` matchers present in `source`.
        For instance, `mtype=url` and `source=matchers` would return
        URL matchers present in the plugin.

        `source` is a variable because we could extract
        matchers from indicators or other attribute too.

        '''
        matchers_dict = getattr(self, source, [])

        return [m[mtype] for m in matchers_dict if mtype in m]

    def get_grouped_matchers(self, source='matchers'):
        """ Return plugin dictionary of matchers (not empty ones)
        with matcher type as key and matcher list as value.

        """
        data = {}
        for k in ['url', 'body', 'header', 'xpath']:
            m = self._get_matchers(k, source)
            if m:
                data[k] = m

        return data

    @property
    def is_version(self):
        return bool(hasattr(self, 'matchers'))

    @property
    def is_modular(self):
        return bool(hasattr(self, 'modular_matchers'))

    @property
    def is_indicator(self):
        return bool(hasattr(self, 'indicators')) and self.ptype == 'normal'

    @property
    def is_js(self):
        return bool(hasattr(self, 'js_matchers'))

    @property
    def is_generic(self):
        return self.ptype == 'generic'


class GenericPlugin(Plugin):
    """ Class used by generic plugins. """
    ptype = 'generic'
