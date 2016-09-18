#!/usr/bin/env python
"""Usage:
    %(script)s <url>
"""
from __future__ import print_function
import os
import subprocess
import sys

try:
    import docopt
    import requests
except ImportError:
    if __name__ != '__main__':
        raise
    try:
        import magicreq
        magicreq.magic(['docopt', 'requests'])
    except ImportError:
        url = 'https://raw.githubusercontent.com/reversefold/magicreq/0.1.0/bootstrap.py'
        # url = 'https://raw.githubusercontent.com/reversefold/magicreq/master/bootstrap.py'
        curl = subprocess.Popen(['curl', '-sS', url], stdout=subprocess.PIPE)
        python = subprocess.Popen([sys.executable, '-'] + sys.argv, stdin=curl.stdout)
        curl.wait()
        python.wait()
        sys.exit(curl.returncode or python.returncode)


def main():
    args = docopt.docopt(__doc__ % {'script': os.path.basename(__file__)})
    print(requests.get(args['<url>']).text)
    sys.exit(13)


if __name__ == '__main__':
    main()
