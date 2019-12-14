import os

from django.conf import settings
from fabric.api import cd, env, get, local, run
from fabric.contrib import django
from prettyconf import config

django.settings_module('base.settings')
_ = settings.INSTALLED_APPS  # fabric bug: https://goo.gl/167WlO

PRODUCTION_HOST = config('PRODUCTION_HOST')
PRODUCTION_BASEDIR = config('PRODUCTION_BASEDIR')
env.hosts = [PRODUCTION_HOST]


def deploy():
    local('git push')
    with cd(PRODUCTION_BASEDIR):
        run('git pull')
        run('pipenv install')
        run('bower install')
        run('pipenv run python manage.py collectstatic --noinput')
        run('pipenv run python manage.py migrate')
        run('supervisorctl restart rq_susikiu')
        run('supervisorctl restart susikiu')


def download_db():
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_name = settings.DATABASES['default']['NAME']

    run('pg_dump --clean --dbname='
        f'postgresql://{db_user}:{db_password}@localhost/{db_name} > '
        '/tmp/susikiu.sql')

    get('/tmp/susikiu.sql', '/tmp')

    local('psql '
          f'--dbname=postgresql://{db_user}:{db_password}@localhost/{db_name} '
          '< /tmp/susikiu.sql')


def download_media():
    media_path = os.path.join(PRODUCTION_BASEDIR, 'media')
    local(f'rsync -rtvu {PRODUCTION_HOST}:{media_path} media/')
