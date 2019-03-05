#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    install_requires=['PyYAML==5.1b3'],
    tests_require=["pytest"],
    setup_requires=['pytest-runner'],

    name='beanstalkio',
    packages=find_packages(),
    version='0.1',
    description='Beanstalkd Python Client',
    author='Christian Kruse',
    author_email='ctkruse99@gmail.com',
)
