import os


def get_boolean_value(key, default):
    value = None
    string_value = os.environ.get(key)

    if string_value == "True":
        value = True
    elif string_value == "False":
        value = False

    if value is None:
        value = default

    return value


PLUGIN_PACKAGES = os.environ.get("DET_PLUGIN_PACKAGES", "detectem.plugins").split(",")

SPLASH_URL = os.environ.get("SPLASH_URL", "http://localhost:8050")
SETUP_SPLASH = get_boolean_value("SETUP_SPLASH", True)
DOCKER_SPLASH_IMAGE = os.environ.get("DOCKER_SPLASH_IMAGE", "scrapinghub/splash:latest")

SPLASH_MAX_TIMEOUT = int(os.environ.get("SPLASH_MAX_TIMEOUT", "120"))
SPLASH_TIMEOUT = 30

DEBUG = get_boolean_value("DEBUG", False)

# CONSTANTS
JSON_OUTPUT = "json"
CMD_OUTPUT = "cmd"

VERSION_TYPE = "version"
INDICATOR_TYPE = "indicator"
HINT_TYPE = "hint"
GENERIC_TYPE = "generic"

RESOURCE_ENTRY = "resource"
MAIN_ENTRY = "main"
INLINE_SCRIPT_ENTRY = "inline-script"
