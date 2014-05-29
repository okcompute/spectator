import os.path
from setuptools import setup


def readfile(name):
    path = os.path.join(os.path.dirname(__file__), name)
    with open(path, 'rb') as stream:
        return stream.read().decode('utf-8')

setup(
    name="spectator",
    version="v0.1",
    author="Andre Caron",
    author_email="andre.l.caron@gmail.com",
    description="Process monitoring tool",
    long_description=readfile('README.rst'),
    license="BSD",
    packages=[
        'spectator',
    ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)
