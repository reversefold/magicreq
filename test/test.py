#!/usr/bin/env python
from __future__ import print_function
import subprocess
import sys

try:
    import requests
except ImportError:
    if __name__ != '__main__':
        raise
    try:
        import magicreq
        magicreq.magic(['requests'])
    except ImportError:
        url = 'https://raw.githubusercontent.com/reversefold/magicreq/0.1.0/bootstrap.py'
        # url = 'https://raw.githubusercontent.com/reversefold/magicreq/master/bootstrap.py'
        curl = subprocess.Popen(['curl', '-sS', url], stdout=subprocess.PIPE)
        python = subprocess.Popen([sys.executable, '-'] + sys.argv, stdin=curl.stdout)
        curl.wait()
        python.wait()
        sys.exit(curl.returncode or python.returncode)

print(requests.get(sys.argv[1]).text)
sys.exit(13)
