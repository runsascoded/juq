from setuptools import setup, find_packages

setup(
    name='juq',
    version='0.0.1',
    packages=find_packages(),
    install_requires=open('requirements.txt').read(),
    entry_points={
        'console_scripts': [
            'juq = juq.cli:cli',
        ],
    },
)
