import os
import pipes
import subprocess
import sys


def magic(requirements):
    if len(sys.argv) > 1 and sys.argv[1] == '--bootstrapped':
        BOOTSTRAPPED = True
        # IN_VENV = True
        sys.argv = [sys.argv[0]] + sys.argv[2:]
    else:
        BOOTSTRAPPED = False
        # if len(sys.argv) > 1 and sys.argv[1] == '--in-venv':
        #     IN_VENV = True
        #     sys.argv = [sys.argv[0]] + sys.argv[2:]
        # else:
        #     IN_VENV = False

    # Bootstrap a python virtualenv which does not rely on any os-level installed packages.
    PY_ENV0_DIR = '_venv'
    VENV_PYTHON = os.path.join(PY_ENV0_DIR, 'bin', 'python')
    # If the virtualenv already appears to exist, try running it without recreating the virtualenv first.
    # If that fails we'll run the script below to fix up the virtualenv.
    # if IN_VENV or not os.path.exists(VENV_PYTHON):
    if not os.path.exists(VENV_PYTHON):
        if not BOOTSTRAPPED:
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
                    python "${VENV_DIRNAME}/virtualenv.py"  --no-pip --no-wheel --no-setuptools --no-site-packages --always-copy "${PY_ENV0_DIR}"
                    curl -sS https://bootstrap.pypa.io/get-pip.py | "${PY_ENV0_DIR}/bin/python" - ${PIP_OPTIONS}
                    "${PY_ENV0_DIR}/bin/pip" install ${PIP_OPTIONS} "${tgz_file}"
                    rm -rf "${VENV_DIRNAME}" "${tgz_file}"

                    . "${PY_ENV0_DIR}/bin/activate"
                    pip install ${PIP_OPTIONS} -U pip setuptools wheel
                """ % (PY_ENV0_DIR,),
                shell=True,
                stdout=sys.stderr
            )
    subprocess.check_call(
        """
            set -ex
            # TODO: Support or remove?
            . "%s/bin/activate"
            PIP_OPTIONS=""
            pip install ${PIP_OPTIONS} %s
        """ % (PY_ENV0_DIR, ' '.join(pipes.quote(r) for r in requirements),),
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
