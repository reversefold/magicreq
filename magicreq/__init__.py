import os
import pipes
import subprocess
import sys


from magicreq import bootstrap


def magic(requirements, pip_options=None, pypi_url=None, venv_version=None, get_pip_url=None):
    if len(sys.argv) > 1 and sys.argv[1] == '--bootstrapped':
        bootstrapped = True
        in_venv = True
        sys.argv = [sys.argv[0]] + sys.argv[2:]
    else:
        bootstrapped = False
        in_venv = os.path.realpath(sys.executable) == os.path.realpath(bootstrap.VENV_PYTHON)

    # Bootstrap a python virtualenv which does not rely on any os-level installed packages.
    # If the virtualenv already appears to exist, try running it without recreating the virtualenv first.
    # If that fails we'll run the script below to fix up the virtualenv.
    if in_venv or not os.path.exists(bootstrap.VENV_PYTHON):
        if not bootstrapped:
            bootstrap.bootstrap(
                pip_options=pip_options,
                pypi_url=pypi_url,
                venv_version=venv_version,
                get_pip_url=get_pip_url
            )
        subprocess.check_call(
            """
                set -e
                PY_ENV0_DIR=%s
                . "${PY_ENV0_DIR}/bin/activate"
                PIP_OPTIONS=%s
                # Note: This is needed to support running magicreq when the path includes a space as
                # the pip script in the virtualenv will have a broken shebang in it.
                function venv_pip() {
                    "${PY_ENV0_DIR}/bin/python" "${PY_ENV0_DIR}/bin/pip" "$@"
                }
                vevv_pip install ${PIP_OPTIONS} %s
            """ % (
                pipes.quote(bootstrap.PY_ENV0_DIR),
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
    #     argv = [bootstrap.VENV_PYTHON, sys.argv[0], '--in-venv'] + sys.argv[1:]
    argv = [bootstrap.VENV_PYTHON] + sys.argv
    os.execv(bootstrap.VENV_PYTHON, argv)
    # should never be called, but include it for safety
    sys.exit(-99)
