import os

PLUGIN_PACKAGES = os.environ.get('DET_PLUGIN_PACKAGES', 'detectem.plugins').split(',')

SPLASH_URL = os.environ.get('SPLASH_URL', 'http://localhost:8050')
SETUP_SPLASH = os.environ.get('SETUP_SPLASH', 'True') == 'True'
DOCKER_SPLASH_IMAGE = os.environ.get('DOCKER_SPLASH_IMAGE', 'scrapinghub/splash:latest')

SPLASH_MAX_TIMEOUT = int(os.environ.get('SPLASH_MAX_TIMEOUT', '120'))
SPLASH_TIMEOUT = 30

JSON_OUTPUT = 'json'
CMD_OUTPUT = 'cmd'

VERSION_TYPE = 'version'
INDICATOR_TYPE = 'indicator'
HINT_TYPE = 'hint'

RESOURCE_ENTRY = 'resource'
MAIN_ENTRY = 'main'
INLINE_SCRIPT_ENTRY = 'inline-script'
