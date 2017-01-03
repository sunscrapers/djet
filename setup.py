import codecs
from setuptools import setup

setup(
    name='djet',
    version='0.2.1',
    description='Set of helpers for easy testing of Django apps.',
    long_description=codecs.open('README.rst', encoding='utf-8').read(),
    license='MIT',
    author='SUNSCRAPERS',
    author_email='info@sunscrapers.com',
    packages=['djet'],
    url='https://github.com/sunscrapers/djet',
    install_requires=[],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing'
    ]
)
