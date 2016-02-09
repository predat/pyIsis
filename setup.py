#!/usr/bin/env python
import os
from setuptools import setup


PKG_NAME = "pyIsis"

def readme():
    with open('README.rst') as f:
        return f.read()

def version():
    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),PKG_NAME,'VERSION')
    with open(version_file,'rb') as fp:
        _version = fp.read().strip()
    return _version

setup(name=PKG_NAME,
      version=version(),
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


