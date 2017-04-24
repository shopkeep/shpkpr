# stdlib imports
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


with open('README.rst') as readme_file:
    readme = readme_file.read()


class Tox(TestCommand):

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, because outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


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
        'chronos-python>=1.0.0',
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
    tests_require=['tox'],
    cmdclass={'test': Tox},
)
