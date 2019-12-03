import glob
import inspect
import logging
import re

from importlib.util import find_spec, module_from_spec

from zope.interface import Attribute, Interface, implementer
from zope.interface.exceptions import BrokenImplementation
from zope.interface.verify import verifyObject

from detectem.settings import PLUGIN_PACKAGES

logger = logging.getLogger("detectem")

LANGUAGE_TAGS = [
    "php",
    "python",
    "ruby",
    "perl",
    "node.js",
    "javascript",
    "asp.net",
    "java",
    "go",
    "ruby on rails",
    "cfml",
]
FRAMEWORK_TAGS = [
    "django",
    "angular",
    "backbone",
    "react",
    "symfony",
    "bootstrap",
    "vue",
    "laravel",
    "woltlab",
    "knockout",
    "ember",
]
PRODUCT_TAGS = [
    "wordpress",
    "mysql",
    "jquery",
    "mootools",
    "apache",
    "iis",
    "nginx",
    "ssl",
    "joomla!",
    "drupal",
    "underscore.js",
    "marionette.js",
    "moment timezone",
    "moment.js",
    "devtools",
    "teamcity",
    "google code prettyfy",
    "solr",
    "postgresql",
    "octopress",
    "k2",
    "sobi 2",
    "sobipro",
    "virtuemart",
    "tomcat",
    "coldfusion",
    "jekill",
    "less",
    "windows server",
    "mysql",
    "waf",
    "webpack",
]
CATEGORY_TAGS = [
    "cms",
    "seo",
    "blog",
    "advertising networks",
    "analytics",
    "wiki",
    "document management system",
    "miscellaneous",
    "message board",
    "angular",
    "js framework",
    "web framework",
    "visualization",
    "graphics",
    "web server",
    "wiki",
    "editor",
    "ecommerce",
    "accounting",
    "database manager",
    "photo gallery",
    "issue tracker",
    "mobile framework",
    "slider",
    "accounting",
    "programming language",
    "hosting panel",
    "lms",
    "js graphic",
    "exhibit",
    "marketing automation",
    "search engine",
    "documentation tool",
    "database",
    "template engine",
    "module bundler",
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

    def with_dom_matchers(self):
        return [p for p in self._plugins.values() if p.is_dom]

    def with_generic_matchers(self):
        return [p for p in self._plugins.values() if p.is_generic]


class _PluginLoader:
    def __init__(self):
        self.plugins = PluginCollection()

    def _full_class_name(self, ins):
        return "{}.{}".format(ins.__class__.__module__, ins.__class__.__name__)

    def _get_plugin_module_paths(self, plugin_dir):
        """ Return a list of every module in `plugin_dir`. """
        filepaths = [
            fp
            for fp in glob.glob("{}/**/*.py".format(plugin_dir), recursive=True)
            if not fp.endswith("__init__.py")
        ]
        rel_paths = [re.sub(plugin_dir.rstrip("/") + "/", "", fp) for fp in filepaths]
        module_paths = [rp.replace("/", ".").replace(".py", "") for rp in rel_paths]

        return module_paths

    def _is_plugin_ok(self, instance):
        """ Return `True` if:
        1. Plugin meets plugin interface.
        2. Is not already registered in the plugin collection.
        3. Have accepted tags.

        Otherwise, return `False` and log warnings.

        """
        try:
            verifyObject(IPlugin, instance)
        except BrokenImplementation:
            logger.warning(
                "Plugin '%(name)s' doesn't provide the plugin interface",
                {"name": self._full_class_name(instance)},
            )
            return False

        # Check if the plugin is already registered
        reg = self.plugins.get(instance.name)
        if reg:
            logger.warning(
                "Plugin '%(name)s' by '%(instance)s' is already provided by '%(reg)s'",
                {
                    "name": instance.name,
                    "instance": self._full_class_name(instance),
                    "reg": self._full_class_name(reg),
                },
            )
            return False

        for tag in instance.tags:
            if tag not in PLUGIN_TAGS:
                logger.warning(
                    "Invalid tag '%(tag)s' in '%(instance)s'",
                    {"tag": tag, "instance": self._full_class_name(instance)},
                )
                return False

        return True

    def load_plugins(self, plugins_package):
        """ Load plugins from `plugins_package` module. """
        try:
            # Resolve directory in the filesystem
            plugin_dir = find_spec(plugins_package).submodule_search_locations[0]
        except ImportError:
            logger.error(
                "Could not load plugins package '%(pkg)s'", {"pkg": plugins_package}
            )
            return

        for module_path in self._get_plugin_module_paths(plugin_dir):
            # Load the module dynamically
            spec = find_spec("{}.{}".format(plugins_package, module_path))
            m = module_from_spec(spec)
            spec.loader.exec_module(m)

            # Get classes from module and extract the plugin classes
            classes = inspect.getmembers(m, predicate=inspect.isclass)
            for _, klass in classes:
                # Avoid imports processing
                if klass.__module__ != spec.name:
                    continue

                # Avoid classes not ending in Plugin
                if not klass.__name__.endswith("Plugin"):
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
    matchers = Attribute(""" List of matchers """)


@implementer(IPlugin)
class Plugin:
    """ Class used by normal plugins.
    It implements :class:`~IPlugin`.

    """

    ptype = "normal"

    def get_matchers(self, matcher_type):
        return [m[matcher_type] for m in self.matchers if matcher_type in m]

    def get_grouped_matchers(self):
        """ Return dictionary of matchers (not empty ones)
        with matcher type as key and matcher list as value.

        """
        data = {}
        for matcher_type in ["url", "body", "header", "xpath", "dom"]:
            matcher_list = self.get_matchers(matcher_type)
            if matcher_list:
                data[matcher_type] = matcher_list

        return data

    @property
    def is_version(self):
        return self.ptype == "normal"

    @property
    def is_dom(self):
        return any([m for m in self.matchers if "dom" in m])

    @property
    def is_generic(self):
        return self.ptype == "generic"


class GenericPlugin(Plugin):
    """ Class used by generic plugins. """

    ptype = "generic"

    def get_information(self, entry):
        raise NotImplementedError()
