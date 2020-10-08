import os
from setuptools import find_packages
from setuptools import setup

with open('VERSION') as file:
    version = file.read().strip()

with open('README.md') as file:
    long_description = file.read()

setup(
    name='python_ci_lib',
    description='Python CI Tools',
    long_description=long_description,
    license='MIT',
    version=version,
    # download_url='',
    author='Ohad Cohen',
    author_email='ohad182@gmail.com',
    maintainer='Ohad Cohen',
    maintainer_email='ohad182@gmail.com',
    url='',
    keywords='',

    packages=find_packages(),
    # package_dir={'execute': 'execute'},
    # include_package_data=True,
    install_requires=[],
    platforms='Platform Independent',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: DevOps',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks']
)
