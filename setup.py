#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requirements = open('requirements.txt').read().splitlines()
test_requirements = open('tests/requirements.txt').read().splitlines()

setup(
    name='detectem',
    version='0.7.0',
    description="Detect software in websites.",
    author="Claudio Salazar",
    author_email='csalazar@spect.cl',
    url='https://github.com/alertot/detectem',
    packages=find_packages(exclude=('tests', 'docs')),
    package_data={'detectem': ['data/*']},
    package_dir={'detectem': 'detectem'},
    entry_points={'console_scripts': ['det=detectem.cli:main']},
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.6',
    license="MIT",
    zip_safe=False,
    keywords='detector detection',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
