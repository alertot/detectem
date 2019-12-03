import glob
import os

from collections import defaultdict

from yaml import FullLoader, load

from detectem.matchers import PluginMatch


def load_from_yaml(test_dir, relative_yaml_file):
    final_path = os.path.join(test_dir, relative_yaml_file)
    lines = []

    if os.path.isdir(final_path):
        for filepath in glob.glob("{}/**.yml".format(final_path)):
            lines += [line for line in load(open(filepath), Loader=FullLoader)]
    else:
        lines = [line for line in load(open(final_path), Loader=FullLoader)]

    return lines


def tree():
    return defaultdict(tree)


def create_pm(name=None, version=None, presence=False):
    return PluginMatch(name, version, presence)
