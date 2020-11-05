from environs import Env

env = Env()
env.read_env()

DEBUG = env.bool("DEBUG", False)
PLUGIN_PACKAGES = env.list("DET_PLUGIN_PACKAGES", "detectem.plugins")

# General Splash configuration
SPLASH_URLS = env.list("SPLASH_URLS", ["http://localhost:8050"])
SETUP_SPLASH = env.bool("SETUP_SPLASH", True)
DOCKER_SPLASH_IMAGE = env("DOCKER_SPLASH_IMAGE", "scrapinghub/splash:latest")
NUMBER_OF_SPLASH_INSTANCES = env.int("NUMBER_OF_SPLASH_INSTANCES", 3)

# Splash internal settings
SPLASH_MAX_TIMEOUT = env.int("SPLASH_MAX_TIMEOUT", 120)
SPLASH_TIMEOUT = 30
SPLASH_MAX_RETRIES = 3


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
