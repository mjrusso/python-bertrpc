from distutils.core import setup

from bertrpc import __version__ as version

setup(
    name = 'bertrpc',
    version = version,
    description = 'BERT-RPC Library',
    author = 'Michael J. Russo',
    author_email = 'mjrusso@gmail.com',
    url = 'http://github.com/mjrusso/python-bertrpc',
    packages = ['bertrpc'],
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
