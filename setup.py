import re
from setuptools import setup

# Load version from module (without loading the whole module)
with open('simongesture/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

# Read in the README.md for the long description.
with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='Simon Gesture',
    version=version,
    url='https://github.com/asweigart/simongesture',
    author='Al Sweigart',
    author_email='al@inventwithpython.com',
    description=('A Simon clone with mouse gestures.'),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='BSD',
    packages=['simongesture'],
    test_suite='tests',
    install_requires=['moosegesture', 'pygame'],
    keywords="game simon mouse gestures",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
