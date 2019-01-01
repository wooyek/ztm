# coding=utf-8
# Copyright (C) 2018 Janusz Skonieczny
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import os
import shutil
import sys
import webbrowser
from collections import OrderedDict
from itertools import chain
from pathlib import Path

# noinspection PyPackageRequirements
from urllib.request import pathname2url

from invoke import call, task

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# logging.getLogger().setLevel(logging.INFO)
# logging.disable(logging.NOTSET)
logging.debug('Loading %s', __name__)

log = logging.getLogger(__name__)

is_win = sys.platform == 'win32'
ROOT_DIR = Path(__file__).parent.absolute()


def get_current_version():
    from configparser import ConfigParser
    cfg = ConfigParser()
    cfg.read(str(Path(ROOT_DIR) / 'setup.cfg'))
    current_version = cfg.get('bumpversion', 'current_version')
    return current_version


# noinspection PyUnusedLocal
@task
def version(ctx):
    print("Version: " + get_current_version())


@task
def clean(ctx):
    """Remote temporary files"""
    for item in chain(Path(ROOT_DIR).rglob("*.pyc"), Path(ROOT_DIR).rglob("*.pyo")):
        logging.debug("Deleting: %s", item)
        item.unlink()

    log.info("Removing __pycache__ in sys.path folders")
    for folder in sys.path:
        for item in Path(folder).rglob("__pycache__"):
            logging.debug("Deleting: %s", item)
            shutil.rmtree(str(item), ignore_errors=True)

    folders = (
        ROOT_DIR / 'build',
        ROOT_DIR / 'example_project' / '.eggs',
        ROOT_DIR / '.eggs',
        ROOT_DIR / '.tox',
        ROOT_DIR / '.tmp',
        ROOT_DIR / '.coverage',
        ROOT_DIR / '.htmlcov',
        ROOT_DIR / '.pytest_cache',
        ROOT_DIR / '.cache',
    )

    for folder in folders:
        print("Removing folder {}".format(folder))
        shutil.rmtree(str(folder), ignore_errors=True)

    ctx.run('git checkout -- .tmp')


@task
def check(ctx):
    """Check project codebase cleanness"""
    ctx.run("flake8 src tests setup.py manage.py")
    ctx.run("isort --check-only --diff --recursive src tests setup.py")
    ctx.run("python setup.py check --strict --metadata --restructuredtext")
    ctx.run("check-manifest  --ignore .idea,.idea/* .")
    ctx.run("pytest --cov=src --cov=tests --cov-fail-under=5")


@task
def coverage(ctx):
    ctx.run("pytest --cov=src --cov=tests --cov-fail-under=5 --cov-report html")
    webbrowser.open("file://" + pathname2url(str(ROOT_DIR / '.tmp' / 'coverage' / 'index.html')))


@task
def isort(ctx):
    """Check project codebase cleanness"""
    ctx.run("isort --recursive src tests setup.py")


@task
def detox(ctx):
    """Run detox with a subset of envs and report run separately"""
    envs = ctx.run("tox -l").stdout.splitlines()
    envs.remove('clean')
    envs.remove('report')
    envs = [e for e in envs if not e.startswith('py2')]
    log.info("Detox a subset of environments: %s", envs)
    ctx.run("tox -e clean")
    ctx.run("detox --skip-missing-interpreters -e " + ",".join(envs))
    ctx.run("tox -e report")


@task
def register_pypi(ctx):
    """Register project on PyPi"""
    ctx.run("git checkout master")
    ctx.run("python setup.py register -r pypi")


@task
def register_pypi_test(ctx):
    """Register project on TEST PyPi"""
    ctx.run("git checkout master")
    ctx.run("python setup.py register -r pypitest")


@task
def upload_pypi(ctx):
    """Upload to PyPi"""
    ctx.run("python setup.py sdist upload -r pypi")
    ctx.run("python setup.py bdist_wheel upload -r pypi")


@task(clean)
def dist(ctx):
    """Build setuptools dist package"""
    ctx.run("python setup.py sdist")
    ctx.run("python setup.py bdist_wheel")
    ctx.run("ls -l dist")


@task(clean)
def install(ctx):
    """Install setuptools dist package"""
    ctx.run("python setup.py install")


@task
def sync(ctx):
    """Sync master and develop branches in both directions"""
    ctx.run("git checkout develop")
    ctx.run("git pull origin develop --verbose")

    ctx.run("git checkout master")
    ctx.run("git pull origin master --verbose")

    ctx.run("git checkout develop")
    ctx.run("git merge master --verbose")

    ctx.run("git checkout develop")


@task(sync)
def sync_master(ctx):
    ctx.run("git checkout master")
    ctx.run("git merge develop --verbose")

    ctx.run("git checkout develop")
    ctx.run("git merge master --verbose")

    ctx.run("git push origin develop --verbose")
    ctx.run("git push origin master --verbose")
    ctx.run("git push --follow-tags")


@task()
def bump(ctx):
    """Increment version number"""
    # ctx.run("bumpversion patch --no-tag")
    ctx.run("bumpversion patch")


@task()
def pip_compile(ctx):
    """Upgrade frozen requirements to the latest version"""
    ctx.run('pip-compile requirements/production.txt -o requirements/lock/production.txt --verbose --upgrade')
    ctx.run('sort requirements/lock/production.txt -o requirements/lock/production.txt')
    ctx.run('git add requirements/lock/*.txt')
    if ctx.run('git diff-index --quiet HEAD', warn=True).exited != 0:
        ctx.run('git commit -m "Requirements compiled by pip-compile" --allow-empty')


@task()
def pipenv(ctx):
    """Upgrade frozen requirements to the latest version"""
    ctx.run('pipenv install -r requirements/production.txt')
    ctx.run('pipenv install --dev -r requirements/development.txt')
    ctx.run('pipenv lock --requirements > requirements/lock/production.txt')
    ctx.run('pipenv lock --requirements --dev | grep -v "/multiinfo-python" -- > requirements/lock/development.txt')
    ctx.run('pipenv graph --reverse -- > requirements/lock/graph.txt')
    ctx.run('sort requirements/lock/production.txt -o requirements/lock/production.txt')
    ctx.run('sort requirements/lock/development.txt -o requirements/lock/development.txt')
    ctx.run('git add Pipfile Pipfile.lock requirements/lock/*.txt')
    ctx.run('git commit -m "Requirements locked by pipenv"')


# noinspection PyUnusedLocal
@task(check, sync, detox)
def release_start(ctx):
    """Start a release cycle with publishing a release branch"""
    ctx.run("git flow release start v{}-release".format(get_current_version()))
    ctx.run("git merge master --verbose")
    ctx.run("bumpversion patch --no-tag --verbose ")
    ctx.run("git flow release --verbose publish")


# noinspection PyUnusedLocal
@task(check, sync, detox, post=[])
def release_finish(ctx):
    """Finish a release cycle with publishing a release branch"""
    ctx.run("git flow release finish --fetch --push")


# noinspection PyUnusedLocal
@task(isort, check, pip_compile, sync, detox, bump, sync_master)
def release(ctx):
    """Build new package version release and sync repo"""


# noinspection PyUnusedLocal
@task(release, post=[upload_pypi])
def publish(ctx):
    """Merge develop, create and upload new version"""
    ctx.run("git checkout master")
    ctx.run("git merge develop --verbose")
