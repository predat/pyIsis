#!/usr/bin/env python
from setuptools import setup
from pyIsis import __version__

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pyIsis',
      version=__version__,
      description='Python wrapper for Avid Isis Client Management Console',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: MacOS X',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Topic :: System :: Systems Administration',
          'Topic :: System :: Filesystems',
          'Topic :: Utilities'
      ],
      keywords='avid isis client mount workspace',
      url='http://github.com/predat/pyIsis',
      author='Sylvain Maziere',
      author_email='sylvain@predat.fr',
      license='MIT',
      packages=['pyIsis'],
      include_package_data=True,
      install_requires=['osa','xmltodict'],
      zip_safe=False)


