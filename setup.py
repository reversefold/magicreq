from setuptools import setup, find_packages

VERSION = '0.6.0'

setup(
    name='magicreq',
    version=VERSION,
    author='Justin Patrin',
    author_email='papercrane@reversefold.com',
    maintainer='Justin Patrin',
    maintainer_email='papercrane@reversefold.com',
    description='magicreq (Magic Requirements): Depend on packages without having to install them.',
    long_description="""magicreq gives you a solution which takes only 15 (or so) lines added to the top of your script which will create a dynamic virtualenv with your specified requirements and automatically re-run the script in that virtualenv. It even works if you haven't installed magicreq.""",
    packages=find_packages(),
    url='https://github.com/reversefold/magicreq',
)
