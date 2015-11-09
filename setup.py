from setuptools import setup

setup(
    name='shpkpr',
    version='0.1',
    packages=['shpkpr', 'shpkpr.commands'],
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        shpkpr=shpkpr.cli:cli
    ''',
)
