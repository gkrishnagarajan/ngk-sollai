#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='ngk-sollai',
    version='1.0.0',
    description='Tamil grammar and spell-correction system for legal judicial documents',
    author='GK Krishnagarajan',
    author_email='gkrish.nagarajan@gmail.com',
    url='https://github.com/gkrishnagarajan/NGK-Solai',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'flask>=2.0.0',
    ],
)
