#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

print("Long descrption:", long_description)
print("Requirements:", requirements)

setup(
    name="textchecker",
    version="0.0.1",
    description="Text checker",
    license="MIT",
    long_description=long_description,
    author="Antoine Mandin",
    author_email="doreapp.contact@gmail.com",
    url="https://github.com/Doreapp/text-checker",
    packages=["textchecker"],
    install_requires=requirements,
    entry_points={
        "console_scripts": ["textchecker=textchecker.__main__"],
    },
)
