from setuptools import setup, find_packages

setup(
    name='juq.py',
    version='0.3.1',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=open('requirements.txt').read(),
    extras_require={
        'test': open('requirements-test.txt').read(),
    },
    license="MIT",
    author="Ryan Williams",
    author_email="ryan@runsascoded.com",
    author_url="https://github.com/ryan-williams",
    url="https://github.com/runsascoded/juq",
    description='Query, run, and clean Jupyter notebooks (name is inspired by "`jq` for Jupyter")',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'juq = juq.main:main',
        ],
    },
)
