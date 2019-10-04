# magicreq

Ever had a python script that you wanted to just work on its own without worrying about whether its dependencies were installed? There are other solutions to this problem, such as packaging the script with its own [virtualenv](https://pypi.python.org/pypi/virtualenv) or using [pex](https://pypi.python.org/pypi/pex) to package everything up in a single executable binary. These solutions work well but only if you want to go through the extra effort of packaging.

magicreq gives you a solution which takes only 15 (or so) lines added to the top of your script which will create a dynamic virtualenv with your specified requirements and automatically re-run the script in that virtualenv. It even works if you haven't installed magicreq.

# Using magicreq

Always make sure to put the magicreq code above any code in the script which performs any work (usually anything other than imports). The reason for this is that magicreq does its magic by re-calling the script multiple times if needed in order to ensure that you have all of your requirements available when the actual script runs. Any code below the magicreq invocation will only ever be run once, though, so don't worry!

There are two main ways to use magicreq which only differ based on what goes into the first `try` block and what you pass to `magicreq.magic()`.

## The import method

If you have a single script you want to convert to using magicreq and don't have a requirements.txt already defined then this method should be easiest to implement. All you have to do is to put your third-party imports into the first `try` block and add a list of the required packages to the `magicreq.magic()` invocation.

```python
#!/usr/bin/env python
from __future__ import print_function

# START boilerplate imports
import os
import sys
try:
    from urllib import request
except ImportError:
    import urllib2 as request
# END boilerplate imports

# put your remaining builtin imports here

# START boilerplate
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
        bootstrap_script = os.path.join(os.getcwd(), '.magicreq_bootstrap.py')
        with open(bootstrap_script, 'wb') as outfile:
            outfile.write(request.urlopen('https://raw.githubusercontent.com/reversefold/magicreq/0.6.0/magicreq/bootstrap.py').read())
        # Run the bootstrap script, replacing the current executable
        os.execv(sys.executable, [sys.executable, bootstrap_script] + sys.argv)
# END boilerplate

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
# put your builtin imports here

# START boilerplate
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
# END boilerplate

# Your script goes here

def main():
    print(requests.get('http://example.org').text)


if __name__ == '__main__':
    main()
```

The imports you put in the first `try` block can be any kind of import for third party libraries, so you can put all of them in that block and not have to re-import anything below the magicreq code.
```python
try:
    import requests
    from docopt import docopt
    import boto.ec2 as boto_ec2
except ImportError:
    ...
```

## The requirements.txt method

If you have a requirements.txt already written for your project or script then the magicreq code becomes entirely boilerplate as you can use the requirements.txt to both check for installed packages and to tell magicreq what needs to be installed.

A small caveat: this method may not work if you have anything in your requirements.txt which is not a requirement (such as including `--index-url` or '-r other_requirements.txt').


```python
#!/usr/bin/env python
from __future__ import print_function
# START boilerplate imports
import os
import sys
try:
    from urllib import request
except ImportError:
    import urllib2 as request
# END boilerplate imports

# put your remaining builtin imports here

# Alter to point to your requirements.txt file
REQUIREMENTS = [line.strip() for line in iter(open('requirements.txt').readline, b'') if line.strip()]

# START boilerplate
try:
    import pkg_resources
    pkg_resources.require(REQUIREMENTS)

# We're expecting ImportError or pkg_resources.ResolutionError but since pkg_resources might not be importable,
# we're just catching Exception.
except Exception as exc:
    if not isinstance(exc, ImportError) and isinstance(exc, pkg_resources.VersionConflict):
        raise
    # Only use magicreq if this is the script being run. Can be omitted if you don't use this file
    # as a module elsewhere.
    if __name__ != '__main__':
        raise
    try:
        # If the current python environment already has magicreq, use it directly
        import magicreq
        magicreq.magic(REQUIREMENTS)
    except ImportError:
        # To support environments without magicreq, this code downloads a bootstrap script which
        # will bootstrap an initial virtualenv with magicreq in it, then re-run this script within
        # the virtualenv.

        # Download the bootstrap script
        bootstrap_script = os.path.join(os.getcwd(), '.magicreq_bootstrap.py')
        with open(bootstrap_script, 'wb') as outfile:
            outfile.write(request.urlopen('https://raw.githubusercontent.com/reversefold/magicreq/0.6.0/magicreq/bootstrap.py').read())
        # Run the bootstrap script, replacing the current executable
        os.execv(sys.executable, [sys.executable, bootstrap_script] + sys.argv)
# END boilerplate

# put your third-party imports here
import requests

# Your script goes here

def main():
    print(requests.get('http://example.org').text)


if __name__ == '__main__':
    main()
```

As above, the last try/except can be reduced if you know for sure that magicreq is installed in the environment where this script will run.


# Advanced configuration

You can also configure how magicreq downloads its files. This can be useful if you have your own mirror of pypi or are using your own artifact storage service (such as S3 or Artifactory). You can even set the version of virtualenv to use for bootstrapping.

```python
...
except Exception as exc:
    if not isinstance(exc, ImportError) and isinstance(exc, pkg_resources.VersionConflict):
        raise
    # You can set any options you want to pass to pip here.
    # This example sets an alternate url for pypi to download packages.
    PIP_OPTIONS = ('--index-url http://my.artifactory.host/artifactory/api/pypi/pypi/simple '
                   '--trusted-host my.artifactory.host')

    # The base pypi URL that will be used for finding and downloading virtualenv
    PYPI_URL = 'http://my.artifactory.host/artifactory/api/pypi/pypi'

    # The version of virtualenv to use
    VENV_VERSION = '15.0.2'

    # The URL to download get-pip.py from
    GET_PIP_URL = 'http://my.artifactory.host/artifactory/static_files/get-pip.py'

    # The URL to magicreq's bootstrap.py
    MAGICREQ_BOOTSTRAP_URL = 'http://my.artifactory.host/artifactory/static_files/magicreq_bootstrap.py'

    if __name__ != '__main__':
        raise
    try:
        import magicreq
        magicreq.magic(
            REQUIREMENTS,

            # These 4 options are passed as keyword arguments here
            pip_options=PIP_OPTIONS,
            pypi_url=PYPI_URL,
            venv_version=VENV_VERSION,
            get_pip_url=GET_PIP_URL
        )
    except ImportError:
        bootstrap_script = os.path.join(os.getcwd(), '.magicreq_bootstrap.py')
        with open(bootstrap_script, 'wb') as outfile:
            outfile.write(request.urlopen(MAGICREQ_BOOTSTRAP_URL).read())
        cmd = [
            sys.executable,
            bootstrap_script,

            # These 4 options are passed with this special format to reduce the requirements
            # of the bootstrapping process.
            'PIP_OPTIONS:%s' % (PIP_OPTIONS,),
            'VENV_VERSION:%s' % (VENV_VERSION,),
            'PYPI_URL:%s' % (PYPI_URL,),
            'GET_PIP_URL:%s' % (GET_PIP_URL,),
        ] + sys.argv
        os.execv(sys.executable, cmd)
```

# How magicreq works
This is a simplified timeline of what happens when a script (named script.py in this example) is run in an environment without magicreq installed.
1. script.py is run with a python executable
2. magicreq is not installed so the bootstrap script gets downloaded and run (via os.execv so it replaces the original process)
3. the bootstrap script bootstraps virtualenv, creates a local virtualenv, and installs magicreq in the virtualenv
4. the bootstrap script reruns script.py with the python executable in the virtualenv (via os.execv, so it replaces the bootstrap script's process)
5. this time, the magicreq.magic method gets called but the requirements are not installed in the virtualenv
6. magicreq installs the requirements into the virtualenv
7. magicreq reruns script.py with the python executable in the virtualenv again (via os.execv, so it replaces the current process)
8. magicreq is installed and all of the requirements are satisfied so the script continues past the boilerplate

At this point, the original python executable has been replaced 3 times and is now running your script within the bootstrapped virtualenv with all of your requirements. The pid should not have changed and any signals sent to the original process should still be caught and processed by your script.


Available on [pypi](https://pypi.python.org/pypi/magicreq).
