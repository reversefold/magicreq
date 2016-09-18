# magicreq

Ever had a python script that you wanted to just work on its own without worrying about whether its dependencies were installed? There are other solutions to this problem, such as packaging the script with its own [virtualenv](https://pypi.python.org/pypi/virtualenv) or using [pex](https://pypi.python.org/pypi/pex) to package everything up in a single executable binary. These solutions work well but only if you want to go through the extra effort of packaging.

magicreq gives you a solution which takes only 15 (or so) lines added to the top of your script which will create a dynamic virtualenv with your specified requirements and automatically re-run the script in that virtualenv. It even works if you haven't installed magicreq.

```python
#!/usr/bin/env python
from __future__ import print_function
import subprocess
import sys
# put your remaining builtin imports here

try:
    # put your third-party imports here
    import requests
except ImportError:
    # Only use magicreq if this is the script being run. Can be omitted if you don't use this file
    # as a module elsewhere.
    if __name__ != '__main__':
        raise
    try:
        # If the current python environment already has magicreq, use it directly
        import magicreq
        magicreq.magic(['requests'])
    except ImportError:
        # To support environments without magicreq, this code downloads a bootstrap script which
        # will bootstrap an initial virtualenv with magicreq in it, then re-run this script within
        # the virtualenv.

        # Download the bootstrap script
        curl = subprocess.Popen(
            ['curl', '-sS', 'https://raw.githubusercontent.com/reversefold/magicreq/0.2.0/bootstrap.py'],
            stdout=subprocess.PIPE
        )
        # pipe the bootstrap script into python
        python = subprocess.Popen([sys.executable, '-'] + sys.argv, stdin=curl.stdout)
        curl.wait()
        python.wait()
        sys.exit(curl.returncode or python.returncode)

# Your script goes here

def main():
    print(requests.get('http://example.org').text)


if __name__ == '__main__':
    main()
```

If you can be sure that your script will be running on a system with at least magicreq installed you can omit the code above that downloads and runs the bootstrap script.

```python
#!/usr/bin/env python
from __future__ import print_function
import subprocess
import sys
# put your remaining builtin imports here

try:
    # put your third-party imports here
    import requests
except ImportError:
    # Only use magicreq if this is the script being run. Can be omitted if you don't use this file
    # as a module elsewhere.
    if __name__ != '__main__':
        raise
    # If the current python environment already has magicreq, use it directly
    import magicreq
    magicreq.magic(['requests'])

# Your script goes here

def main():
    print(requests.get('http://example.org').text)


if __name__ == '__main__':
    main()
```

Always make sure to put the magicreq code above any code in the script which performs any work. The reason for this is that magicreq does its magic by re-calling the script multiple times if needed in order to ensure that you have all of your requirements available when the actual script runs. Any code below the magicreq invocation will only ever be run once, though so don't worry!

The imports you put in the first `try` block can be any kind of import for third party libraries, so you can put all of them in that block and not have to re-import anything below the magicreq code.
```python
try:
    import requests
    from docopt import docopt
    import boto.ec2 as boto_ec2
except ImportError:
    ...
```