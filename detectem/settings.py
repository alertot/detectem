import os


SPLASH_URL = os.environ.get('SPLASH_URL', 'http://localhost:8050')
SETUP_SPLASH = os.environ.get('SETUP_SPLASH', 'True') == 'True'
DOCKER_SPLASH_IMAGE = os.environ.get('DOCKER_SPLASH_IMAGE', 'scrapinghub/splash:latest')
