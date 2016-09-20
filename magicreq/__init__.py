import os
import pipes
import subprocess
import sys


def magic(requirements, pip_options=''):
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
            subprocess.check_call(
                """
                    set -e
                    VENV_VERSION="15.0.3"
                    # This appears to be a new pypi layout which may or may not be predictable.
                    # Check that this works when updating VENV_VERSION
                    PYPI_VENV_BASE="https://pypi.python.org/packages/8b/2c/c0d3e47709d0458816167002e1aa3d64d03bdeb2a9d57c5bd18448fd24cd"
                    PY_ENV0_DIR="%s"
                    rm -rf "${PY_ENV0_DIR}"

                    PIP_OPTIONS=%s

                    VENV_DIRNAME="virtualenv-${VENV_VERSION}"
                    tgz_file="${VENV_DIRNAME}.tar.gz"
                    venv_url="${PYPI_VENV_BASE}/${tgz_file}"

                    curl -sS -O "${venv_url}"
                    tar xzf "${tgz_file}"
                    python "${VENV_DIRNAME}/virtualenv.py"  --no-pip --no-wheel --no-setuptools --no-site-packages --always-copy "${PY_ENV0_DIR}"
                    curl -sS https://bootstrap.pypa.io/get-pip.py | "${PY_ENV0_DIR}/bin/python" - ${PIP_OPTIONS}
                    "${PY_ENV0_DIR}/bin/pip" install ${PIP_OPTIONS} "${tgz_file}"
                    rm -rf "${VENV_DIRNAME}" "${tgz_file}"

                    . "${PY_ENV0_DIR}/bin/activate"
                    pip install ${PIP_OPTIONS} -U pip setuptools wheel
                    pip install ${PIP_OPTIONS} -U magicreq
                """ % (PY_ENV0_DIR, pipes.quote(pip_options)),
                shell=True,
                stdout=sys.stderr
            )
        subprocess.check_call(
            """
                set -e
                . "%s/bin/activate"
                PIP_OPTIONS=%s
                pip install ${PIP_OPTIONS} %s
            """ % (PY_ENV0_DIR, pipes.quote(pip_options), ' '.join(pipes.quote(r) for r in requirements),),
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
