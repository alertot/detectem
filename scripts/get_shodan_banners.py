import os
import pprint
import re
import sys

import click

try:
    import shodan
except ImportError:
    print('Install shodan: pip install shodan')
    sys.exit(0)

try:
    SHODAN_API_KEY = os.environ['SHODAN_API_KEY']
except KeyError:
    print('Set SHODAN_API_KEY environment variable with your key')
    sys.exit(0)


def get_headers(text):
    header_string = re.findall('^(.*?)(?:[\r\n]{3,4})', text, flags=re.DOTALL | re.I)
    if not header_string:
        return None

    data = {}
    for line in header_string[0].splitlines():
        match = re.findall('^(.*?):(.*)', line)

        if match:
            key, value = map(lambda v: v.strip(), match[0])
            data[key] = value

    return data


@click.command()
@click.option('--filter', default=None, type=str, help='Filter by header')
@click.option('--stats', default=False, is_flag=True, help='Include stats')
@click.option('--show-names', default=False, is_flag=True, help='Show header names')
@click.argument('query')
def main(filter, stats, show_names, query):
    counter = 0
    filtered_header = set()
    api = shodan.Shodan(SHODAN_API_KEY)

    try:
        result = api.search(query)
    except shodan.exception.APIError:
        print('[-] API connection error.')
        sys.exit(0)

    for match in result['matches']:
        server = '{}:{}'.format(match['ip_str'], match['port'])
        hd = get_headers(match['data'])
        if not hd:
            continue

        if show_names:
            filtered_header.update(set(hd.keys()))
        elif filter:
            value = hd.get(filter)
            if value:
                filtered_header.add((server, value))
        else:
            pprint.pprint(hd, width=160)
            counter += 1

    if filtered_header:
        pprint.pprint(filtered_header, width=160)

    if stats:
        print('\n--- Stats ---')
        print('[+] n_matches: {}'.format(len(result['matches'])))
        print('[+] n_printed: {}'.format(counter or len(filtered_header)))


if __name__ == '__main__':
    main()
