from setuptools import setup

setup(
    name='shpkpr',
    version='0.1',
    packages=['shpkpr', 'shpkpr.commands'],
    include_package_data=True,
    install_requires=[
        'cached-property==1.3.0',
        'click==6.0',
        'dcos==0.2.0',
        'jinja2==2.8',
        'six>=1.10.0',
        'requests>=2.0.0',
    ],
    entry_points='''
        [console_scripts]
        shpkpr=shpkpr.cli:cli
    ''',
)
