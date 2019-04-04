#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-zafira',
    version='1.0.0',
    author='Vadim Delendik',
    author_email='vdelendik@qaprosoft.com',
    maintainer='Vadim Delendik',
    maintainer_email='vdelendik@qaprosoft.com',
    license='Apache Software License 2.0',
    url='https://github.com/qaprosoft/zafira-pytest',
    description='A Zafira plugin for pytest',
    long_description=read('README.rst'),
    packages=find_packages(),
    py_modules=['pytest_zafira'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    install_requires=[
        'allure-python-commons==2.5.4',
        'atomicwrites==1.2.1',
        'attrs==18.2.0',
        'boto3==1.9.106',
        'botocore==1.12.106',
        'certifi==2018.11.29',
        'chardet==3.0.4',
        'configparser==3.5.0',
        'docutils==0.14',
        'idna==2.8',
        'jmespath==0.9.4',
        'more-itertools==4.3.0',
        'pika==0.12.0',
        'pluggy==0.7.1',
        'py==1.6.0',
        'pytest==4.1.1',
        'python-dateutil==2.8.0',
        'PyYAML==3.13',
        'requests==2.21.0',
        's3transfer==0.2.0',
        'selenium==3.14.0',
        'six==1.11.0',
        'urllib3==1.23',
    ],
    keywords=['pytest', 'zafira'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
    ],
    entry_points={
        'pytest11': [
            'zafira = pytest_zafira',
        ],
    },
)
