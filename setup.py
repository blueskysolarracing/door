#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name='door',
    version='0.0.3',
    description='A comprehensive python library for synchronization proxies',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    url='https://github.com/blueskysolarracing/door',
    author='Blue Sky Solar Racing',
    author_email='blueskysolar@studentorg.utoronto.ca',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords=['python', 'synchronization'],
    project_urls={
        'Documentation': 'https://door.readthedocs.io/en/latest/',
        'Source': 'https://github.com/blueskysolarracing/door',
        'Tracker': 'https://github.com/blueskysolarracing/door/issues',
    },
    packages=find_packages(),
    python_requires='>=3.11',
    package_data={'door': ['py.typed']},
)
