#!/usr/bin/env python
"""Usage:
    %(script)s <url>
"""
from __future__ import print_function
import os
import subprocess
import sys

REQUIREMENTS = [line.strip() for line in iter(open('requirements.txt').readline, '') if line.strip()]

try:
    import pkg_resources
    pkg_resources.require(REQUIREMENTS)
    # import docopt
    # import requests
except Exception as exc:
    # PIP_OPTIONS = '--index-url http://localhost:8080/pypi/simple/ --trusted-host localhost'
    # VENV_VERSION = '15.0.2'
    # PYPI_URL = 'http://localhost:8080/api/pypi/pypi'
    # GET_PIP_URL = 'http://localhost:8080/get-pip.py'
    if __name__ != '__main__':
        raise
    try:
        import magicreq
        magicreq.magic(
            ['docopt', 'requests'],
            # pip_options=PIP_OPTIONS,
            # pypi_url=PYPI_URL,
            # venv_version=VENV_VERSION,
            # get_pip_url=GET_PIP_URL
        )
    except ImportError:
        url = 'https://raw.githubusercontent.com/reversefold/magicreq/0.4.0/magicreq/bootstrap.py'
        # url = 'https://raw.githubusercontent.com/reversefold/magicreq/master/magicreq/bootstrap.py'
        # url = 'http://localhost:8000/magicreq/bootstrap.py'
        curl = subprocess.Popen(['curl', '-sS', url], stdout=subprocess.PIPE)
        python = subprocess.Popen(
            [
                sys.executable,
                '-',
                # 'PIP_OPTIONS:%s' % (PIP_OPTIONS,),
                # 'VENV_VERSION:%s' % (VENV_VERSION,),
                # 'PYPI_URL:%s' % (PYPI_URL,),
                # 'GET_PIP_URL:%s' % (GET_PIP_URL,),
            ] + sys.argv,
            stdin=curl.stdout
        )
        curl.wait()
        python.wait()
        sys.exit(curl.returncode or python.returncode)


def main():
    args = docopt.docopt(__doc__ % {'script': os.path.basename(__file__)})
    print(requests.get(args['<url>']).text)
    sys.exit(13)


if __name__ == '__main__':
    main()
