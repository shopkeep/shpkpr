# stdlib imports
from setuptools import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()




setup(
    name='shpkpr',
    version='0.1',
    description='shpkpr is a command-line tool designed to manage applications running on Marathon',
    long_description=readme,
    author='ShopKeep.com Inc.',
    author_email='developers@shopkeep.com',
    url='https://github.com/shopkeep/shpkpr',
    packages=['shpkpr', 'shpkpr.cli', 'shpkpr.commands', 'shpkpr.marathon'],
    package_data={'shpkpr': ['marathon/schema/*.json']},
    include_package_data=True,
    install_requires=[
        'cached-property>=1.3.0, <2',
        'chronos-python>=0.35.0, <1.0.0',
        'click>=6.0, <7',
        'jinja2>=2.6, <3',
        'jsonschema>=2.6, <3',
        'six>=1, <2',
        'requests>=2, <3',
    ],
    license='MIT',
    zip_safe=False,
    keywords='shpkpr mesos marathon',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points='''
        [console_scripts]
        shpkpr=shpkpr.cli.entrypoint:cli
    ''',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'mock',
        'pytest',
        'responses',
    ],
)
