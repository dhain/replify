#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


_dir = os.path.dirname(__file__)
readme = open(os.path.join(_dir, 'README.rst')).read()
history = open(os.path.join(_dir, 'HISTORY.rst')).read().replace(
    '.. :changelog:', '')


setup_args = dict(
    name='replify',
    version='0.1.0',

    description='Make a Python code snippet look like it was typed at the REPL',
    long_description=readme + '\n\n' + history,

    author='David Zuwenden',
    author_email='david@zuwenden.org',
    url='https://github.com/dhain/replify',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    keywords='replify',

    packages=[
        'replify',
        'replify.test',
    ],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
    ],

    test_suite='replify.test',
    test_loader='replify.test.loader:Loader',
    tests_require=[
    ],

    entry_points={
        'console_scripts': [
            'replify = replify.replify:main',
        ],
    },
)


if __name__ == '__main__':
    setup(**setup_args)
