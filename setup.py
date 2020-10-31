#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
        'pyglet<2',
        ]

setup_requirements = [ ]

test_requirements = [
    'pytest',
]

setup(
    author="Yehuda Garti",
    author_email='yeudag@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    description="Block Puzzle game made using Pyglet",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='pyglet_block_puzzle',
    name='pyglet_block_puzzle',
    packages=find_packages(include=['pyglet_block_puzzle', 'pyglet_block_puzzle.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/yegarti/pyglet_block_puzzle',
    version='0.1.0',
    zip_safe=False,
)
