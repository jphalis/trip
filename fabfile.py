# https://github.com/joke2k/django-environ
# http://cookiecutter-django.readthedocs.io/en/latest/deployment-on-heroku.html

import dotenv

from fabric.api import local, task
from fabric.colors import cyan as _cyan, green as _green, yellow as _yellow
from fabric.operations import prompt


@task
def deploy():
    """Deploys the latest files to the production server."""
    local('python manage.py makemigrations')
    local('python manage.py migrate')
    local('git add .')
    msg = prompt("Enter your git commit message: ")
    local('git commit -m "{}"'.format(msg))
    _push_bitbucket()
    # _push_heroku()
    print(_green('Successfully pushed project', bold=True))


def _push_bitbucket():
    """Push the latest code to BitBucket."""
    print(_yellow('Pushing to origin master...', bold=True))
    local('git push -u origin master')


def _push_heroku():
    """Push the latest code to Heroku."""
    print(_cyan('Maintenance mode on.'))
    local('heroku maintenance:on')
    print(_yellow('Pushing to Heroku...', bold=True))
    local('git push heroku master')
    local('heroku maintenance:off')
    print(_cyan('Maintenance mode off.'))


@task
def config_heroku_env_vars():
    dotenv.read_dotenv(set_heroku=True)
