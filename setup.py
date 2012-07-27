#!/usr/bin/env python

from setuptools import setup

setup(
    name='watcard',
    version='0.1.0',
    description="Work with transaction and balance data from University of Waterloo's Watcard",
    author='Ansis Brammanis',
    author_email='ansis.brammanis@gmail.com',
    license='MIT',
    url='https://github.com/ansis/watcard',
    download_url='https://github.com/ansis/watcard/tarball/master',
    py_modules=['watcard'],
    install_requires=(
        'tablib',
        'BeautifulSoup',
    ),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    )
)
