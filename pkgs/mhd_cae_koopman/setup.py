# -*- coding: utf-8 -*-

from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='mhd_cae_koopman',
    version='0.0.1',
    author='Michael Skowronek',
    author_email='michael.skowronek.91@gmail.com',
    maintainer='Michael Skowronek',
    maintainer_email='michael.skowronek.91@gmail.com',
    description="Python package for mhd_cae_koopman.",
    long_description="Python package for mhd_cae_koopman.",
    install_requires=requirements,
    python_requires=">=3.12",
    package_dir = {
        'mhd_cae_koopman': 'src/mhd_cae_koopman',
    }
)