import os
import pipes
import subprocess
import sys


from magicreq import bootstrap


def magic(requirements, pip_options=None, pypi_url=None, venv_version=None):
    PY_ENV0_DIR = '_venv'
    VENV_PYTHON = os.path.join(PY_ENV0_DIR, 'bin', 'python')
    if len(sys.argv) > 1 and sys.argv[1] == '--bootstrapped':
        BOOTSTRAPPED = True
        IN_VENV = True
        sys.argv = [sys.argv[0]] + sys.argv[2:]
    else:
        BOOTSTRAPPED = False
        if os.path.realpath(sys.executable) == os.path.realpath(VENV_PYTHON):
            IN_VENV = True
        else:
            IN_VENV = False

    # Bootstrap a python virtualenv which does not rely on any os-level installed packages.
    # If the virtualenv already appears to exist, try running it without recreating the virtualenv first.
    # If that fails we'll run the script below to fix up the virtualenv.
    # if IN_VENV or not os.path.exists(VENV_PYTHON):
    if IN_VENV or not os.path.exists(VENV_PYTHON):
        if not BOOTSTRAPPED:
            bootstrap.bootstrap(pip_options=pip_options, pypi_url=pypi_url, venv_version=venv_version)
        subprocess.check_call(
            """
                set -e
                . %s/bin/activate
                PIP_OPTIONS=%s
                pip install ${PIP_OPTIONS} %s
            """ % (
                pipes.quote(PY_ENV0_DIR),
                pipes.quote(pip_options if pip_options is not None else ''),
                ' '.join(pipes.quote(r) for r in requirements),
            ),
            shell=True,
            stdout=sys.stderr
        )
    # call this script again using the virtualenv's python
    # if os.path.basename(sys.argv[0]) == 'python':
    #     argv = [sys.argv[0], '--in-venv'] + sys.argv[1:]
    # else:
    #     argv = [VENV_PYTHON, sys.argv[0], '--in-venv'] + sys.argv[1:]
    argv = [VENV_PYTHON] + sys.argv
    os.execv(VENV_PYTHON, argv)
    # should never be called, but include it for safety
    sys.exit(-99)
