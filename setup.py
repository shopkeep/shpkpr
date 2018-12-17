# stdlib imports
from setuptools import find_packages
from setuptools import setup


try:
    with open('README.rst') as readme_file:
        readme = readme_file.read()
except IOError:
    # README is not always available at the time this file is imported. This
    # really only applies during an initial container build when we copy in
    # setup.py but not the README. This is mostly to help with caching and
    # keeping the time required to run the tests to a minimum. This should never
    # make it into an actual build or release package.
    readme = "Not Available"


setup(
    name='shpkpr',
    version='4.1.2',
    description='shpkpr is a command-line tool designed to manage applications running on Marathon',
    long_description=readme,
    author='ShopKeep.com Inc.',
    author_email='developers@shopkeep.com',
    url='https://github.com/shopkeep/shpkpr',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyYAML>=3.10.0',
        'cached-property>=1.3.0, <2',
        'chronos-python>=1.1.0',
        'click>=6.0, <7',
        'docker>=3.0.0',
        'hvac>=0.2.17',
        'jinja2>=2.6, <3',
        'jsonschema>=2.6, <3',
        'python-slugify>=1.2.4',
        'six>=1.11.0',
        'requests>=2.4.2',
    ],
    license='MIT',
    zip_safe=False,
    keywords='shpkpr mesos marathon chronos',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    entry_points='''
        [console_scripts]
        shpkpr=shpkpr.cli.entrypoint:cli
    ''',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'freezegun',
        'mock',
        'pytest',
        'responses',
    ],
)
