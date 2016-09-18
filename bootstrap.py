from __future__ import print_function
import os
import subprocess
import sys

print(sys.argv)

# Bootstrap a python virtualenv which does not rely on any os-level installed packages.
PY_ENV0_DIR = '_venv'
VENV_PYTHON = os.path.join(PY_ENV0_DIR, 'bin', 'python')
subprocess.check_call(
    """
        set -ex
        VENV_VERSION="15.0.2"
        # This appears to be a new pypi layout which may or may not be predictable.
        # Check that this works when updating VENV_VERSION
        PYPI_VENV_BASE="https://pypi.python.org/packages/5c/79/5dae7494b9f5ed061cff9a8ab8d6e1f02db352f3facf907d9eb614fb80e9"

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
