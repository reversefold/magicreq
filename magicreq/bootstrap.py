from __future__ import print_function
from xml.etree import ElementTree
import os
import pipes
import subprocess
import sys
import urllib2


PY_ENV0_DIR = '_venv'
PY_ENV0_BIN = os.path.join(PY_ENV0_DIR, 'bin')
VENV_PYTHON = os.path.join(PY_ENV0_BIN, 'python')
PIP_OPTIONS_PREFIX = 'PIP_OPTIONS'
VENV_VERSION_PREFIX = 'VENV_VERSION'
PYIPI_URL_PREFIX = 'PYPI_URL'
GET_PIP_URL_PREFIX = 'GET_PIP_URL'


class Error(Exception):
    pass


# Bootstrap a python virtualenv which does not rely on any os-level installed packages.
def bootstrap(pip_options=None, venv_version=None, pypi_url=None, get_pip_url=None):
    if pip_options is None:
        pip_options = ''
    if venv_version is None:
        venv_version = '16.0.0'
    if pypi_url is None:
        pypi_url = 'https://pypi.org'
    if get_pip_url is None:
        get_pip_url = 'https://bootstrap.pypa.io/get-pip.py'

    # TODO: Automatically put pypi_url in pip_options?

    venv_dirname = 'virtualenv-%s' % (venv_version,)
    venv_file = '%s.tar.gz' % (venv_dirname,)

    # Note: Would use the json or xmlrpc APIs but we need to use the simple API to support artifactory
    tree = ElementTree.parse(urllib2.urlopen('%s/simple/virtualenv/' % (pypi_url,)))
    found = [a for a in tree.getroot().find('body').findall('a') if a.text == venv_file]
    if not found:
        raise Error('Could not find virtualenv version %r with pypi url %r' % (venv_version, pypi_url))
    href = found[0].attrib['href']
    if not href.startswith('../../'):
        raise Error('Found virtualenv href does not start with "../../": %r' % (href,))
    venv_url = '%s/%s' % (pypi_url, href[6:])

    subprocess.check_call(
        """
            set -ex
            PY_ENV0_DIR=%s
            PIP_OPTIONS=%s
            VENV_DIRNAME=%s
            VENV_FILE=%s
            VENV_URL=%s
            GET_PIP_URL=%s
            # Note: This is needed to support running magicreq when the path includes a space as
            # the pip script in the virtualenv will have a broken shebang in it.
            venv_pip() {
                "${PY_ENV0_DIR}/bin/python" "${PY_ENV0_DIR}/bin/pip" "$@"
            }

            rm -rf "${PY_ENV0_DIR}" "${VENV_DIRNAME}" "${VENV_FILE}"

            curl -sS "${VENV_URL}" > "${VENV_FILE}"
            tar xzf "${VENV_FILE}"
            python "${VENV_DIRNAME}/virtualenv.py" --no-pip --no-wheel --no-setuptools --no-site-packages --always-copy "${PY_ENV0_DIR}"
            curl -sS "${GET_PIP_URL}" | "${PY_ENV0_DIR}/bin/python" - ${PIP_OPTIONS}
            venv_pip install ${PIP_OPTIONS} "${VENV_FILE}"
            rm -rf "${VENV_DIRNAME}" "${VENV_FILE}"

            . "${PY_ENV0_DIR}/bin/activate"
            venv_pip install ${PIP_OPTIONS} -U pip setuptools wheel
            venv_pip install ${PIP_OPTIONS} -U magicreq
        """ % (
            pipes.quote(PY_ENV0_DIR),
            pipes.quote(pip_options),
            pipes.quote(venv_dirname),
            pipes.quote(venv_file),
            pipes.quote(venv_url),
            pipes.quote(get_pip_url),
        ),
        shell=True,
        stdout=sys.stderr
    )


def main():
    kwargs = {}
    found = True
    while found:
        found = False
        for prefix in [
            PIP_OPTIONS_PREFIX, VENV_VERSION_PREFIX, PYIPI_URL_PREFIX, GET_PIP_URL_PREFIX
        ]:
            if len(sys.argv) > 1 and sys.argv[1].startswith(prefix):
                found = True
                kwargs[prefix.lower()] = sys.argv[1][len(prefix) + 1:]
                sys.argv = sys.argv[0:1] + sys.argv[2:]

    bootstrap(**kwargs)
    # update the PATH to include the virtualenv's bin directory
    os.environ['PATH'] = os.pathsep.join(
        [PY_ENV0_BIN]
        + os.environ.get('PATH', '').split(os.pathsep)
    )
    # call this script again using the virtualenv's python
    os.execv(VENV_PYTHON, [VENV_PYTHON, sys.argv[1], '--bootstrapped'] + sys.argv[2:])
    # should never be called, but include it for safety
    sys.exit(-99)


if __name__ == '__main__':
    main()
