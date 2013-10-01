#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='pyjenkins',
    version='0.1.2',
    description='Python wrapper around the Jenkins JSON API',
    long_description=readme + '\n\n' + history,
    author='Chris Lawlor',
    author_email='chris.lawlor@stylecaster.com',
    url='https://github.com/stylecaster/pyjenkins',
    packages=[
        'pyjenkins',
    ],
    package_dir={'pyjenkins': 'pyjenkins'},
    include_package_data=True,
    install_requires=[
        'requests >= 2.0.0'
    ],
    license="MIT",
    zip_safe=False,
    keywords='jenkins',
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
    test_suite='tests',
)
