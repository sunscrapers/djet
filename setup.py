from setuptools import setup

requires = [
    'Django>=1.3'
]

setup(
    name='djet',
    version='0.0.4',
    description='TestCase extension for Django views unit testing.',
    long_description=open('README.rst').read(),
    author='SUNSCRAPERS',
    author_email='info@sunscrapers.com',
    packages=['djet'],
    url='https://github.com/sunscrapers/djet',
    install_requires=requires,
)
