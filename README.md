# magicreq

Ever had a python script that you wanted to just work on its own without worrying about whether its dependencies were installed? There are other solutions to this problem, such as packaging the script with its own [virtualenv](https://pypi.python.org/pypi/virtualenv) or using [pex](https://pypi.python.org/pypi/pex) to package everything up in a single executable binary. These solutions work well but only if you want to go through the extra effort of packaging.

magicreq gives you a solution which takes only 15 (or so) lines added to the top of your script which will create a dynamic virtualenv with your specified requirements and automatically re-run the script in that virtualenv. It even works if you haven't installed magicreq.

```python
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
        curl = subprocess.Popen(['curl', '-sS', 'https://raw.githubusercontent.com/reversefold/magicreq/0.1.0/bootstrap.py'], stdout=subprocess.PIPE)
        python = subprocess.Popen([sys.executable, '-'] + sys.argv, stdin=curl.stdout)
        curl.wait()
        python.wait()
        sys.exit(curl.returncode or python.returncode)

print(requests.get(sys.argv[1]).text)
sys.exit(13)
```
