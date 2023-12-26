from setuptools import setup, find_packages

setup(
    name='juq.py',
    version='0.0.1',
    packages=find_packages(),
    install_requires=open('requirements.txt').read(),
    license="MIT",
    author="Ryan Williams",
    author_email="ryan@runsascoded.com",
    author_url="https://github.com/ryan-williams",
    url="https://github.com/runsascoded/juq",
    description='CLI for viewing/slicing Jupyter notebooks (name is inspired by "`jq` for Jupyter")',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'juq = juq.cli:cli',
        ],
    },
)
