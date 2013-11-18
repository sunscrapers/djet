from setuptools import setup

requires = [
    'Django>=1.3',
    'six>=1.4.1',
]

setup(
    name='djet',
    version='0.0.7',
    description='TestCase extension for Django views unit testing.',
    long_description=open('README.rst').read(),
    license='MIT',
    author='SUNSCRAPERS',
    author_email='info@sunscrapers.com',
    packages=['djet'],
    url='https://github.com/sunscrapers/djet',
    install_requires=requires,
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
