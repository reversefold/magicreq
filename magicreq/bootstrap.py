from __future__ import print_function
from xml.etree import ElementTree
import os
import pipes
import subprocess
import sys
import urllib2


PY_ENV0_DIR = '_venv'
VENV_PYTHON = os.path.join(PY_ENV0_DIR, 'bin', 'python')
PIP_OPTIONS_PREFIX = 'PIP_OPTIONS:'


class Error(Exception):
    pass


# Bootstrap a python virtualenv which does not rely on any os-level installed packages.
def bootstrap(pip_options=None, venv_version=None, pypi_url=None):
    if pip_options is None:
        pip_options = ''
    if venv_version is None:
        venv_version = '15.0.3'
    if pypi_url is None:
        pypi_url = 'https://pypi.python.org'

    # TODO: Automatically put pypi_url in pip_options?

    VENV_DIRNAME = 'virtualenv-%s' % (venv_version,)
    tgz_file = '%s.tar.gz' % (VENV_DIRNAME,)

    # Note: Would use the json or xmlrpc APIs but we need to use the simple API to support artifactory
    tree = ElementTree.parse(urllib2.urlopen('%s/simple/virtualenv/' % (pypi_url,)))
    found = [a for a in tree.getroot().find('body').findall('a') if a.text == tgz_file]
    if not found:
        raise Error('Could not find virtualenv version %r with pypi url %r' % (venv_version, pypi_url))
    href = found[0].attrib['href']
    if not href.startswith('../../'):
        raise Error('Found virtualenv href does not start with "../../": %r' % (href,))
    venv_url = '%s/%s' % (pypi_url, href[6:])

    subprocess.check_call(
        """
            set -e
            PY_ENV0_DIR=%s
            PIP_OPTIONS=%s
            VENV_DIRNAME=%s
            tgz_file=%s
            venv_url=%s

            rm -rf "${PY_ENV0_DIR}" "${VENV_DIRNAME}" "${tgz_file}"

            curl -sS "${venv_url}" > "${tgz_file}"
            tar xzf "${tgz_file}"
            python "${VENV_DIRNAME}/virtualenv.py" --no-pip --no-wheel --no-setuptools --no-site-packages --always-copy "${PY_ENV0_DIR}"
            curl -sS https://bootstrap.pypa.io/get-pip.py | "${PY_ENV0_DIR}/bin/python" - ${PIP_OPTIONS}
            "${PY_ENV0_DIR}/bin/pip" install ${PIP_OPTIONS} "${tgz_file}"
            rm -rf "${VENV_DIRNAME}" "${tgz_file}"

            . "${PY_ENV0_DIR}/bin/activate"
            pip install ${PIP_OPTIONS} -U pip setuptools wheel
            pip install ${PIP_OPTIONS} -U magicreq
        """ % (
            pipes.quote(PY_ENV0_DIR),
            pipes.quote(pip_options),
            pipes.quote(VENV_DIRNAME),
            pipes.quote(tgz_file),
            pipes.quote(venv_url),
        ),
        shell=True,
        stdout=sys.stderr
    )


def main():
    if len(sys.argv) > 1 and sys.argv[1].startswith(PIP_OPTIONS_PREFIX):
        PIP_OPTIONS = sys.argv[1][len(PIP_OPTIONS_PREFIX):]
        sys.argv = sys.argv[0:1] + sys.argv[2:]
    else:
        PIP_OPTIONS = ''
    bootstrap(pip_options=PIP_OPTIONS)
    # call this script again using the virtualenv's python
    os.execv(VENV_PYTHON, [VENV_PYTHON, sys.argv[1], '--bootstrapped'] + sys.argv[2:])
    # should never be called, but include it for safety
    sys.exit(-99)


if __name__ == '__main__':
    main()
