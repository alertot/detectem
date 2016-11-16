import os

import click


@click.command()
@click.option(
    '--matcher',
    type=click.Choice(['url', 'body', 'header']),
    required=True,
    help='Set the matcher type.',
)
@click.option(
    '--value',
    type=str,
    required=True,
    help='Set the matcher value.',
)
@click.option(
    '--category',
    type=click.Choice(['frontend', 'backend', 'wordpress', 'infraestructure']),
    required=True,
    help='Set plugin category.',
)
@click.argument('name')
def main(name, category, matcher, value):
    directory = os.path.dirname(__file__)
    if matcher == 'header':
        value = tuple(value.split(','))

    create_plugin_file(directory, name, category, matcher, value)
    create_test_file(directory, name, matcher)


def create_plugin_file(directory, name, category, matcher, value):
    plugin_template = '''
from detectem.plugin import Plugin


class {title}Plugin(Plugin):
    name = '{name}'
    matchers = [
        {{'{matcher}': '{value}'}},
    ]
'''.format(name=name, title=name.title(), matcher=matcher, value=value).lstrip()

    plugin_filename = name + '.py'
    plugin_filepath = os.path.abspath(
        os.path.join(directory, '..', 'detectem', 'plugins', category, plugin_filename)
    )

    if os.path.exists(plugin_filepath):
        raise FileExistsError('Plugin file already exists.')

    with open(plugin_filepath, mode='w') as f:
        f.write(plugin_template)
        print('Created plugin file at {}'.format(plugin_filepath))


def create_test_file(directory, name, matcher):
    test_template = '''
- plugin: {name}
  matches:
    - {matcher}:
      version:
'''.format(name=name, matcher=matcher).lstrip()

    test_filename = name + '.yml'
    test_filepath = os.path.abspath(
        os.path.join(directory, '..', 'tests', 'plugins', 'fixtures', test_filename)
    )

    if os.path.exists(test_filepath):
        raise FileExistsError('Test file already exists.')

    with open(test_filepath, mode='w') as f:
        f.write(test_template)
        print('Created test file at {}'.format(test_filepath))

if __name__ == "__main__":
    main()
