from __future__ import print_function
import os
import subprocess
import sys

# Bootstrap a python virtualenv which does not rely on any os-level installed packages.
PY_ENV0_DIR = '_venv'
VENV_PYTHON = os.path.join(PY_ENV0_DIR, 'bin', 'python')
subprocess.check_call(
    """
        set -e
        VENV_VERSION="15.0.3"
        # This appears to be a new pypi layout which may or may not be predictable.
        # Check that this works when updating VENV_VERSION
        PYPI_VENV_BASE="https://pypi.python.org/packages/8b/2c/c0d3e47709d0458816167002e1aa3d64d03bdeb2a9d57c5bd18448fd24cd"

        PY_ENV0_DIR="%s"
        rm -rf "${PY_ENV0_DIR}"

        # TODO: Support or remove?
        PIP_OPTIONS=""

        VENV_DIRNAME="virtualenv-${VENV_VERSION}"
        tgz_file="${VENV_DIRNAME}.tar.gz"
        venv_url="${PYPI_VENV_BASE}/${tgz_file}"

        curl -sS -O "${venv_url}"
        tar xzf "${tgz_file}"
        python "${VENV_DIRNAME}/virtualenv.py" --no-pip --no-wheel --no-setuptools --no-site-packages --always-copy "${PY_ENV0_DIR}"
        curl -sS https://bootstrap.pypa.io/get-pip.py | "${PY_ENV0_DIR}/bin/python" - ${PIP_OPTIONS}
        "${PY_ENV0_DIR}/bin/pip" install ${PIP_OPTIONS} "${tgz_file}"
        rm -rf "${VENV_DIRNAME}" "${tgz_file}"

        . "${PY_ENV0_DIR}/bin/activate"
        pip install ${PIP_OPTIONS} -U pip setuptools wheel
        pip install ${PIP_OPTIONS} magicreq
    """ % (PY_ENV0_DIR,),
    shell=True
)

# call this script again using the virtualenv's python
os.execv(VENV_PYTHON, [VENV_PYTHON, sys.argv[1], '--bootstrapped'] + sys.argv[2:])
# should never be called, but include it for safety
sys.exit(-99)
