import os
import re
import io
import zipfile
import tempfile
import hashlib
import pprint
import logging

import requests
import click
import click_log

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

FILE_REGEX = r'^v?(\d+\.\d+\.?\d+?)$'  # avoid beta releases
N_RESULTS = 100


def get_files_from_github(user_and_repo, filedir):
    ''' Return dictionary of version:directory and directory has extracted files. '''
    github_url = f'https://api.github.com/repos/{user_and_repo}'
    args = f'?per_page={N_RESULTS}'
    results = []

    # Determine the right url
    url = f'{github_url}/releases{args}'
    json_data = requests.get(url).json()
    if not json_data:
        url = f'{github_url}/tags{args}'
        json_data = requests.get(url).json()

    logger.debug(f'[+] Using {url} as base url.')

    # Get all the releases/tags available
    results = json_data
    for n_page in range(2, 1000):
        logger.debug(f'[+] Requesting page {n_page} of releases/tags ..')
        json_data = requests.get(f'{url}&page={n_page}').json()
        results += json_data

        if len(json_data) < N_RESULTS:
            break

    if not results:
        raise ValueError(f'No releases/tags for {user_and_repo}')

    directories = {}
    for result in results:
        name = result['name']
        m = re.match(FILE_REGEX, name)
        if not m:
            continue

        name = m.groups()[0]

        logger.debug(f'[+] Downloading zip file for {name} version ..')

        # Download zip file and extract in temporary directory
        zip_url = result['zipball_url']
        zf = requests.get(zip_url, allow_redirects=True)
        z = zipfile.ZipFile(io.BytesIO(zf.content))
        output_dir = f'{filedir}/{z.namelist()[0]}'

        z.extractall(path=filedir)
        directories[name] = output_dir

    return directories


@click.command()
@click.option('--github', default=None, type=str, help='user/repository')
@click_log.simple_verbosity_option(logger, default='error')
@click.argument('filepath', type=str)
def main(github, filepath):
    with tempfile.TemporaryDirectory() as filedir:
        logger.debug(f'[+] Using {filedir} as temporary directory.')

        directories = []
        if github:
            directories = get_files_from_github(github, filedir)

        logger.debug('[+] Creating hashes ..')

        hashes = {}
        for version, path in directories.items():
            target_file = os.path.join(path, filepath)
            with open(target_file) as f:
                content = f.read().encode('utf-8')
                m = hashlib.sha256()
                m.update(content)
                h = m.hexdigest()
                hashes[version] = h

        pprint.pprint({filepath: hashes})


if __name__ == '__main__':
    main()
